import io
import os
import tempfile
import uuid
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import pytest
from asn1crypto import x509 as asn1_x509
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID
from fastapi.testclient import TestClient
from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter
from pyhanko.sign import signers
from reportlab.pdfgen import canvas

from app.core.database import SessionLocal
from app.integrations.verification.signed_pdf_adapter import SignedPdfVerificationAdapter
from app.main import app
from app.models.application import Application
from app.models.application_document import ApplicationDocument
from app.models.document import Document
from app.models.manual_review import ManualReview
from app.models.scholarship import Scholarship
from app.models.student import Student
from app.models.user import User
from app.models.verification_record import VerificationRecord
from app.services.verification_service import execute_verification

client = TestClient(app)

# -------------------------------------------------------------
# TEST ROOT CA SETUP
# -------------------------------------------------------------
_test_ca_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
_test_ca_name = x509.Name([
    x509.NameAttribute(NameOID.COMMON_NAME, "Test Indian CCA Root"),
    x509.NameAttribute(NameOID.ORGANIZATION_NAME, "India PKI"),
    x509.NameAttribute(NameOID.COUNTRY_NAME, "IN"),
])
_test_ca_cert = (
    x509.CertificateBuilder()
    .subject_name(_test_ca_name)
    .issuer_name(_test_ca_name)
    .public_key(_test_ca_key.public_key())
    .serial_number(1)
    .not_valid_before(datetime.now(timezone.utc) - timedelta(days=1))
    .not_valid_after(datetime.now(timezone.utc) + timedelta(days=3650))
    .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
    .sign(_test_ca_key, hashes.SHA256())
)
_asn1_test_ca = asn1_x509.Certificate.load(_test_ca_cert.public_bytes(serialization.Encoding.DER))
SignedPdfVerificationAdapter.extra_trust_roots = [_asn1_test_ca]


def generate_signed_pdf(
    file_path: str,
    name: str = "Asha Meena",
    dob: str = "15/08/2004",
    income: int = 240000,
    signer_cn: str = "DigiLocker CA",
    signer_org: str = "National e-Governance Division",
    self_signed: bool = False,
):
    """Generates a real digitally signed PDF file with certificate text and embedded signature."""
    # 1. Create PDF with text
    pdf_buf = io.BytesIO()
    c = canvas.Canvas(pdf_buf)
    c.drawString(100, 750, "Government of India - DigiLocker Official Certificate")
    c.drawString(100, 720, f"Name: {name}")
    c.drawString(100, 700, f"Date of Birth: {dob}")
    c.drawString(100, 680, f"Annual Family Income: Rs {income:,}")
    c.showPage()
    c.save()

    # 2. Generate RSA Key & X509 Certificate
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    subject = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, signer_cn),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, signer_org),
    ])

    with tempfile.NamedTemporaryFile(suffix=".pem") as kf, tempfile.NamedTemporaryFile(suffix=".pem") as cf, tempfile.NamedTemporaryFile(suffix=".pem") as caf:
        kf.write(
            key.private_bytes(
                serialization.Encoding.PEM,
                serialization.PrivateFormat.PKCS8,
                serialization.NoEncryption(),
            )
        )
        kf.flush()

        if self_signed:
            # Self-signed certificate (not issued by trusted CA)
            cert = (
                x509.CertificateBuilder()
                .subject_name(subject)
                .issuer_name(subject)
                .public_key(key.public_key())
                .serial_number(x509.random_serial_number())
                .not_valid_before(datetime.now(timezone.utc) - timedelta(days=1))
                .not_valid_after(datetime.now(timezone.utc) + timedelta(days=365))
                .add_extension(
                    x509.KeyUsage(
                        digital_signature=True,
                        content_commitment=True,
                        key_encipherment=False,
                        data_encipherment=False,
                        key_agreement=False,
                        key_cert_sign=False,
                        crl_sign=False,
                        encipher_only=False,
                        decipher_only=False,
                    ),
                    critical=True,
                )
                .sign(key, hashes.SHA256())
            )
            cf.write(cert.public_bytes(serialization.Encoding.PEM))
            cf.flush()
            signer = signers.SimpleSigner.load(key_file=kf.name, cert_file=cf.name)
        else:
            # Certificate issued by Test Indian CCA Root
            cert = (
                x509.CertificateBuilder()
                .subject_name(subject)
                .issuer_name(_test_ca_name)
                .public_key(key.public_key())
                .serial_number(x509.random_serial_number())
                .not_valid_before(datetime.now(timezone.utc) - timedelta(days=1))
                .not_valid_after(datetime.now(timezone.utc) + timedelta(days=365))
                .add_extension(
                    x509.KeyUsage(
                        digital_signature=True,
                        content_commitment=True,
                        key_encipherment=False,
                        data_encipherment=False,
                        key_agreement=False,
                        key_cert_sign=False,
                        crl_sign=False,
                        encipher_only=False,
                        decipher_only=False,
                    ),
                    critical=True,
                )
                .sign(_test_ca_key, hashes.SHA256())
            )
            cf.write(cert.public_bytes(serialization.Encoding.PEM))
            cf.flush()
            caf.write(_test_ca_cert.public_bytes(serialization.Encoding.PEM))
            caf.flush()
            signer = signers.SimpleSigner.load(key_file=kf.name, cert_file=cf.name, ca_chain_files=[caf.name])

        pdf_buf.seek(0)
        with open(file_path, "wb") as out_f:
            signers.sign_pdf(
                IncrementalPdfFileWriter(pdf_buf),
                signers.PdfSignatureMetadata(field_name="DigiLockerSignature"),
                signer=signer,
                output=out_f,
            )


@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as td:
        yield td


@pytest.fixture
def db_session():
    db = SessionLocal()
    yield db
    db.close()


# -------------------------------------------------------------
# 1. SIGNATURE VALIDATION & TAMPER DETECTION TESTS
# -------------------------------------------------------------

def test_signed_pdf_verified_and_matching(temp_dir):
    pdf_path = os.path.join(temp_dir, "income_cert.pdf")
    generate_signed_pdf(pdf_path, name="Asha Meena", dob="15/08/2004", income=240000)

    student = Student(
        name="Asha Meena",
        date_of_birth=date(2004, 8, 15),
        annual_family_income=240000,
    )
    doc = Document(
        document_type="INCOME_CERTIFICATE",
        document_name="income_cert.pdf",
        file_path=pdf_path,
        source="PDF_UPLOAD",
    )

    result = SignedPdfVerificationAdapter.verify_document(doc, student=student)
    assert result["status"] == "VERIFIED"
    assert result["evaluation_mode"] == "SIGNED_PDF"
    assert "DigiLocker" in result["signer_name"]


def test_signed_pdf_fuzzy_name_matching(temp_dir):
    pdf_path = os.path.join(temp_dir, "income_cert_fuzzy.pdf")
    generate_signed_pdf(pdf_path, name="Asha Meena", dob="15/08/2004", income=240000)

    # Profile has transliteration variation "Asha Mina"
    student = Student(
        name="Asha Mina",
        date_of_birth=date(2004, 8, 15),
        annual_family_income=240000,
    )
    doc = Document(
        document_type="INCOME_CERTIFICATE",
        document_name="income_cert.pdf",
        file_path=pdf_path,
        source="PDF_UPLOAD",
    )

    result = SignedPdfVerificationAdapter.verify_document(doc, student=student)
    assert result["status"] == "VERIFIED"
    assert result["evaluation_mode"] == "SIGNED_PDF"


def test_signed_pdf_tampered_fails(temp_dir):
    pdf_path = os.path.join(temp_dir, "valid_cert.pdf")
    generate_signed_pdf(pdf_path, name="Asha Meena", dob="15/08/2004", income=240000)

    # Tamper with 1 byte of the signed PDF
    with open(pdf_path, "rb") as f:
        data = bytearray(f.read())
    data[120] ^= 0xFF  # Flip bits of one byte

    tampered_path = os.path.join(temp_dir, "tampered_cert.pdf")
    with open(tampered_path, "wb") as f:
        f.write(data)

    student = Student(name="Asha Meena")
    doc = Document(
        document_type="INCOME_CERTIFICATE",
        document_name="tampered_cert.pdf",
        file_path=tampered_path,
        source="PDF_UPLOAD",
    )

    result = SignedPdfVerificationAdapter.verify_document(doc, student=student)
    assert result["status"] == "FAILED"
    assert result["evaluation_mode"] == "SIGNED_PDF"
    assert "modified after signing" in result["message"] or "invalid" in result["message"]


def test_unsigned_pdf_fails(temp_dir):
    unsigned_path = os.path.join(temp_dir, "unsigned.pdf")
    c = canvas.Canvas(unsigned_path)
    c.drawString(100, 750, "Name: Asha Meena")
    c.showPage()
    c.save()

    doc = Document(
        document_type="ST_CERTIFICATE",
        document_name="unsigned.pdf",
        file_path=unsigned_path,
        source="PDF_UPLOAD",
    )
    result = SignedPdfVerificationAdapter.verify_document(doc, student=Student(name="Asha Meena"))
    assert result["status"] == "FAILED"
    assert "Digital signature missing" in result["message"]


def test_signed_pdf_data_mismatch(temp_dir):
    pdf_path = os.path.join(temp_dir, "mismatch_cert.pdf")
    generate_signed_pdf(pdf_path, name="Ramesh Kumar", dob="15/08/2004", income=240000)

    # Student name is Asha Meena
    student = Student(
        name="Asha Meena",
        date_of_birth=date(2004, 8, 15),
        annual_family_income=240000,
    )
    doc = Document(
        document_type="INCOME_CERTIFICATE",
        document_name="mismatch_cert.pdf",
        file_path=pdf_path,
        source="PDF_UPLOAD",
    )

    result = SignedPdfVerificationAdapter.verify_document(doc, student=student)
    assert result["status"] == "MISMATCH"
    assert result["evaluation_mode"] == "SIGNED_PDF"
    assert "Name on certificate 'Ramesh Kumar' does not match profile 'Asha Meena'" in result["message"]


def test_signed_pdf_untrusted_signer_fails(temp_dir):
    pdf_path = os.path.join(temp_dir, "untrusted_cert.pdf")
    generate_signed_pdf(pdf_path, signer_cn="Untrusted Fake CA", signer_org="Untrusted Entity")

    student = Student(name="Asha Meena")
    doc = Document(
        document_type="ST_CERTIFICATE",
        document_name="untrusted_cert.pdf",
        file_path=pdf_path,
        source="PDF_UPLOAD",
    )

    result = SignedPdfVerificationAdapter.verify_document(doc, student=student)
    assert result["status"] == "FAILED"
    assert "not in the trusted signers list" in result["message"]


def test_self_signed_cert_with_trusted_cn_fails(temp_dir):
    """A PDF signed with a self-signed certificate whose CN matches a trusted name
    must FAIL with reason 'Certificate not issued by a trusted Indian CA'."""
    pdf_path = os.path.join(temp_dir, "fake_digilocker.pdf")
    generate_signed_pdf(
        pdf_path,
        name="Asha Meena",
        signer_cn="DigiLocker CA",
        signer_org="National e-Governance Division",
        self_signed=True,
    )

    student = Student(name="Asha Meena")
    doc = Document(
        document_type="ST_CERTIFICATE",
        document_name="fake_digilocker.pdf",
        file_path=pdf_path,
        source="PDF_UPLOAD",
    )

    result = SignedPdfVerificationAdapter.verify_document(doc, student=student)
    assert result["status"] == "FAILED"
    assert result["message"] == "Certificate not issued by a trusted Indian CA"
    assert result["evaluation_mode"] == "SIGNED_PDF"


# -------------------------------------------------------------
# 2. REAL MARKSHEET SAMPLE TEST (IF EXISTS)
# -------------------------------------------------------------

def test_real_marksheet_sample_if_present():
    sample_path = Path("tests/samples/real_marksheet.pdf")
    if not sample_path.exists():
        pytest.skip("backend/tests/samples/real_marksheet.pdf not found (skipped as instructed)")

    doc = Document(
        document_type="CLASS_12_MARKSHEET",
        document_name="real_marksheet.pdf",
        file_path=str(sample_path),
        source="PDF_UPLOAD",
    )
    result = SignedPdfVerificationAdapter.verify_document(doc)
    assert result["evaluation_mode"] == "SIGNED_PDF"


# -------------------------------------------------------------
# 3. UPLOAD API ENDPOINT TESTS
# -------------------------------------------------------------

def test_api_upload_document(db_session, temp_dir):
    # 1. Create user and student
    u = User(name="Upload Student", email=f"upload_{uuid.uuid4().hex[:6]}@example.com", password="pw")
    db_session.add(u)
    db_session.commit()
    db_session.refresh(u)

    st = Student(name="Upload Student", email=u.email, user_id=u.id)
    db_session.add(st)
    db_session.commit()
    db_session.refresh(st)

    # 2. Create sample PDF
    pdf_path = os.path.join(temp_dir, "test_upload.pdf")
    generate_signed_pdf(pdf_path, name="Upload Student")

    with open(pdf_path, "rb") as f:
        file_bytes = f.read()

    # 3. Test successful upload
    response = client.post(
        f"/api/v1/students/{st.id}/documents/upload",
        files={"file": ("test_upload.pdf", file_bytes, "application/pdf")},
        data={"document_type": "INCOME_CERTIFICATE"},
    )
    assert response.status_code == 200
    doc_json = response.json()
    assert doc_json["student_id"] == st.id
    assert doc_json["document_type"] == "INCOME_CERTIFICATE"
    assert doc_json["source"] == "PDF_UPLOAD"
    assert doc_json["file_path"] is not None
    assert os.path.exists(doc_json["file_path"])

    # 4. Test invalid document_type
    bad_type_res = client.post(
        f"/api/v1/students/{st.id}/documents/upload",
        files={"file": ("test.pdf", b"%PDF-1.4 dummy", "application/pdf")},
        data={"document_type": "INVALID_TYPE"},
    )
    assert bad_type_res.status_code == 400
    assert "Invalid document_type" in bad_type_res.json()["detail"]

    # 5. Test non-PDF upload
    non_pdf_res = client.post(
        f"/api/v1/students/{st.id}/documents/upload",
        files={"file": ("test.txt", b"plain text content", "text/plain")},
        data={"document_type": "INCOME_CERTIFICATE"},
    )
    assert non_pdf_res.status_code == 400
    assert "Only PDF files are allowed" in non_pdf_res.json()["detail"]

    # 6. Test file > 5 MB
    large_bytes = b"%PDF-1.4 " + b"0" * (5 * 1024 * 1024 + 10)
    large_res = client.post(
        f"/api/v1/students/{st.id}/documents/upload",
        files={"file": ("large.pdf", large_bytes, "application/pdf")},
        data={"document_type": "INCOME_CERTIFICATE"},
    )
    assert large_res.status_code == 400
    assert "exceeds maximum limit of 5 MB" in large_res.json()["detail"]


# -------------------------------------------------------------
# 4. EXECUTE VERIFICATION WORKFLOW WITH PDF_UPLOAD
# -------------------------------------------------------------

def test_execute_verification_with_pdf_upload(db_session, temp_dir):
    # 1. Setup Student, Scholarship, Application
    user = User(name="Verify User", email=f"ver_{uuid.uuid4().hex[:6]}@example.com", password="pw")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    student = Student(
        name="Asha Meena",
        email=user.email,
        user_id=user.id,
        date_of_birth=date(2004, 8, 15),
        annual_family_income=240000,
    )
    db_session.add(student)
    db_session.commit()
    db_session.refresh(student)

    scholarship = db_session.query(Scholarship).first()

    app_rec = Application(student_id=student.id, scholarship_id=scholarship.id, status="DRAFT")
    db_session.add(app_rec)
    db_session.commit()
    db_session.refresh(app_rec)

    # 2. Upload Document
    pdf_path = os.path.join(temp_dir, "asha_cert.pdf")
    generate_signed_pdf(pdf_path, name="Asha Meena", dob="15/08/2004", income=240000)

    doc = Document(
        student_id=student.id,
        document_type="INCOME_CERTIFICATE",
        document_name="asha_cert.pdf",
        file_path=pdf_path,
        source="PDF_UPLOAD",
        status="PENDING",
    )
    db_session.add(doc)
    db_session.commit()
    db_session.refresh(doc)

    # Link document to application
    link = ApplicationDocument(application_id=app_rec.id, document_id=doc.id)
    db_session.add(link)
    db_session.commit()

    # 3. Create Verification Record
    ver = VerificationRecord(application_id=app_rec.id, document_id=doc.id, status="PENDING")
    db_session.add(ver)
    db_session.commit()
    db_session.refresh(ver)

    # 4. Execute verification
    exec_res = execute_verification(db_session, ver.id)
    assert exec_res["status"] == "VERIFIED"
    assert exec_res["evaluation_mode"] == "SIGNED_PDF"

    # Refresh verification from DB
    db_session.refresh(ver)
    assert ver.status == "VERIFIED"


# -------------------------------------------------------------
# 5. LEGACY MOCK VERIFICATION FLOW
# -------------------------------------------------------------

def test_old_mock_verification_flow_still_works(db_session):
    """Ensure documents without source='PDF_UPLOAD' (e.g. MOCK, DIGILOCKER_MOCK)
    continue using the deterministic MockVerificationAdapter."""
    user = User(name="Mock User", email=f"mock_{uuid.uuid4().hex[:6]}@example.com", password="pw")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    student = Student(name="Mock Student", email=user.email, user_id=user.id)
    db_session.add(student)
    db_session.commit()
    db_session.refresh(student)

    scholarship = db_session.query(Scholarship).first()
    app_rec = Application(student_id=student.id, scholarship_id=scholarship.id, status="DRAFT")
    db_session.add(app_rec)
    db_session.commit()
    db_session.refresh(app_rec)

    # 1. Document with source='MOCK' and TEST_VERIFIED
    doc_mock = Document(
        student_id=student.id,
        document_type="TEST_VERIFIED",
        document_name="mock_doc.pdf",
        file_path=None,
        source="MOCK",
        status="PENDING",
    )
    db_session.add(doc_mock)
    db_session.commit()
    db_session.refresh(doc_mock)

    link = ApplicationDocument(application_id=app_rec.id, document_id=doc_mock.id)
    db_session.add(link)
    db_session.commit()

    ver = VerificationRecord(application_id=app_rec.id, document_id=doc_mock.id, status="PENDING")
    db_session.add(ver)
    db_session.commit()
    db_session.refresh(ver)

    res = execute_verification(db_session, ver.id)
    assert res["status"] == "VERIFIED"
    assert res["evaluation_mode"] == "MOCK"
    assert "Mock document successfully verified" in res["message"]

    # 2. Document with source='DIGILOCKER_MOCK' and TEST_FAILED
    doc_fail = Document(
        student_id=student.id,
        document_type="TEST_FAILED",
        document_name="mock_fail.pdf",
        file_path=None,
        source="DIGILOCKER_MOCK",
        status="PENDING",
    )
    db_session.add(doc_fail)
    db_session.commit()
    db_session.refresh(doc_fail)

    link_fail = ApplicationDocument(application_id=app_rec.id, document_id=doc_fail.id)
    db_session.add(link_fail)
    db_session.commit()

    ver_fail = VerificationRecord(application_id=app_rec.id, document_id=doc_fail.id, status="PENDING")
    db_session.add(ver_fail)
    db_session.commit()
    db_session.refresh(ver_fail)

    res_fail = execute_verification(db_session, ver_fail.id)
    assert res_fail["status"] == "FAILED"
    assert res_fail["evaluation_mode"] == "MOCK"
