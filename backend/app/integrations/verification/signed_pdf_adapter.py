import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any

import pdfplumber
from pyhanko.pdf_utils.reader import PdfFileReader
from pyhanko.sign.validation import validate_pdf_signature
from pyhanko_certvalidator import ValidationContext
from rapidfuzz import fuzz

EVALUATION_MODE = "SIGNED_PDF"

# Certificates directories for Indian CCA Root Certificates and Intermediate CAs
TRUST_ROOTS_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "trust_roots"
INTERMEDIATES_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "intermediates"


def format_inr(number: int) -> str:
    """Format an integer in the Indian numbering format (e.g. 2,50,000)."""
    s = str(abs(number))
    if len(s) <= 3:
        formatted = s
    else:
        last_three = s[-3:]
        remaining = s[:-3]
        parts = []
        while len(remaining) > 2:
            parts.append(remaining[-2:])
            remaining = remaining[:-2]
        if remaining:
            parts.append(remaining)
        parts.reverse()
        formatted = ",".join(parts) + "," + last_three
    return f"-{formatted}" if number < 0 else formatted


def get_trusted_signers() -> list[str]:
    """Load trusted signer names from environment variable TRUSTED_SIGNERS."""
    env_signers = os.getenv("TRUSTED_SIGNERS", "")
    if not env_signers:
        # Default known trusted Indian certificate authorities / DigiLocker
        return [
            "digilocker",
            "national e-governance division",
            "controller of certifying authorities",
            "emudhra",
            "capricorn",
            "nsdl",
            "vsign",
            "nic",
        ]
    return [s.strip().lower() for s in env_signers.split(",") if s.strip()]


def _load_certs_from_directory(directory: Path) -> list:
    """Load x509 certificates (DER or PEM) from a given directory."""
    import base64
    from asn1crypto import x509 as asn1_x509

    certs = []
    if not directory.exists():
        return certs
    for cert_file in sorted(directory.glob("*")):
        if cert_file.suffix.lower() not in [".cer", ".crt", ".pem"]:
            continue
        try:
            with open(cert_file, "rb") as f:
                content = f.read().strip()
            if b"-----BEGIN CERTIFICATE-----" in content:
                for chunk in content.split(b"-----BEGIN CERTIFICATE-----")[1:]:
                    b64_part = chunk.split(b"-----END CERTIFICATE-----")[0]
                    clean_b64 = b"".join(b64_part.split())
                    der = base64.b64decode(clean_b64)
                    certs.append(asn1_x509.Certificate.load(der))
            else:
                try:
                    certs.append(asn1_x509.Certificate.load(content))
                except Exception:
                    der = base64.b64decode(b"".join(content.split()))
                    certs.append(asn1_x509.Certificate.load(der))
        except Exception:
            continue
    return certs


def load_cca_validation_context(
    extra_trust_roots: list | None = None,
    extra_intermediates: list | None = None,
    moment: datetime | None = None,
) -> ValidationContext | None:
    """Load Indian CCA root certificates from TRUST_ROOTS_DIR and intermediates from INTERMEDIATES_DIR."""
    roots_dir = Path(os.getenv("TRUST_ROOTS_DIR", str(TRUST_ROOTS_DIR)))
    trust_roots = _load_certs_from_directory(roots_dir)

    if extra_trust_roots:
        trust_roots.extend(extra_trust_roots)
    if hasattr(SignedPdfVerificationAdapter, "extra_trust_roots") and SignedPdfVerificationAdapter.extra_trust_roots:
        trust_roots.extend(SignedPdfVerificationAdapter.extra_trust_roots)

    inter_dir = Path(os.getenv("INTERMEDIATES_DIR", str(INTERMEDIATES_DIR)))
    other_certs = _load_certs_from_directory(inter_dir)

    if extra_intermediates:
        other_certs.extend(extra_intermediates)
    if hasattr(SignedPdfVerificationAdapter, "extra_intermediates") and SignedPdfVerificationAdapter.extra_intermediates:
        other_certs.extend(SignedPdfVerificationAdapter.extra_intermediates)

    if trust_roots:
        return ValidationContext(
            trust_roots=trust_roots,
            other_certs=other_certs if other_certs else None,
            allow_fetching=True,
            revocation_mode="soft-fail",
            moment=moment,
            retroactive_revinfo=True,
        )
    return None


def extract_certificate_data(pdf_path: str) -> dict[str, Any]:
    """Extract candidate text, name, date of birth, and income using pdfplumber."""
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = "\n".join(page.extract_text() or "" for page in pdf.pages)
    except Exception:
        pass

    extracted: dict[str, Any] = {
        "text": text,
        "name": None,
        "date_of_birth": None,
        "annual_family_income": None,
    }

    if not text:
        return extracted

    # 1. Extract Name
    name_patterns = [
        r"(?:Candidate\s*Name|Student\s*Name|Name\s*of\s*(?:the\s*)?(?:Candidate|Student|Applicant)|Name)\s*[:\-]\s*([A-Za-z\.\'\t ]+)",
        r"(?:This\s+is\s+to\s+certify\s+that|Certified\s+that)\s+(?:Shri|Smt|Kumari|Mr\.|Ms\.)?\s*([A-Za-z\.\'\t ]+?)(?:\s*(?:\n|\r|\Z)|(?:\s+(?:S/o|D/o|W/o|son\s+of|daughter\s+of|bearing|resident|has|is|,)))",
    ]
    for pattern in name_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            candidate = match.group(1).strip()
            candidate = re.sub(r"\s+", " ", candidate).strip()
            if len(candidate) > 2 and not any(kw in candidate.lower() for kw in ["certify", "signature", "date"]):
                extracted["name"] = candidate
                break

    # 2. Extract Date of Birth
    dob_patterns = [
        r"(?:Date\s*of\s*Birth|DOB|Birth\s*Date)\s*[:\-]?\s*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}|\d{4}[\/\-\.]\d{1,2}[\/\-\.]\d{1,2})",
        r"(?:born\s*on)\s*[:\-]?\s*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}|\d{4}[\/\-\.]\d{1,2}[\/\-\.]\d{1,2})",
    ]
    for pattern in dob_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            extracted["date_of_birth"] = match.group(1).strip()
            break

    # 3. Extract Income (for income certificates)
    income_patterns = [
        r"(?:Annual\s*Family\s*Income|Annual\s*Income|Family\s*Income|Total\s*(?:Annual\s*)?Income|Income\s*from\s*all\s*sources)\s*[:\-]?\s*(?:Rs\.?|INR|₹)?\s*([\d,]+)",
    ]
    for pattern in income_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            raw_inc = match.group(1).replace(",", "").strip()
            if raw_inc.isdigit():
                extracted["annual_family_income"] = int(raw_inc)
                break

    return extracted


def normalize_dob(dob_str: str) -> str:
    """Normalize date string to YYYY-MM-DD or comparable digits."""
    digits = re.findall(r"\d+", str(dob_str))
    if len(digits) == 3:
        # Check if year is first or last
        if len(digits[0]) == 4:  # YYYY-MM-DD
            return f"{digits[0]}-{int(digits[1]):02d}-{int(digits[2]):02d}"
        elif len(digits[2]) == 4:  # DD-MM-YYYY
            return f"{digits[2]}-{int(digits[1]):02d}-{int(digits[0]):02d}"
    return "".join(digits)


def check_dob_match(extracted_dob: str, profile_dob: Any) -> bool:
    """Compare extracted date of birth with profile date of birth."""
    norm_ext = normalize_dob(extracted_dob)
    norm_prof = normalize_dob(str(profile_dob))
    return norm_ext == norm_prof


class SignedPdfVerificationAdapter:
    """Real document verification adapter using pyHanko and pdfplumber for digitally signed PDFs."""

    extra_trust_roots: list = []

    @classmethod
    def verify_document(cls, document, student=None) -> dict[str, Any]:
        file_path = getattr(document, "file_path", None)
        if not file_path or not os.path.exists(file_path):
            return {
                "status": "FAILED",
                "message": "Document file not found on disk",
                "evaluation_mode": EVALUATION_MODE,
            }

        # 1. Inspect digital signatures with pyHanko
        try:
            with open(file_path, "rb") as f:
                reader = PdfFileReader(f)
                embedded_sigs = reader.embedded_signatures
                if not embedded_sigs:
                    return {
                        "status": "FAILED",
                        "message": "Digital signature missing from PDF",
                        "evaluation_mode": EVALUATION_MODE,
                    }

                sig = embedded_sigs[0]
                signing_time = getattr(sig, "self_reported_timestamp", None)
                validation_context = load_cca_validation_context(moment=signing_time)

                try:
                    val_status = validate_pdf_signature(
                        sig,
                        signer_validation_context=validation_context,
                    )
                except Exception as val_err:
                    err_str = str(val_err)
                    if "self-signed" in err_str.lower() or "no issuer" in err_str.lower() or "path" in err_str.lower():
                        return {
                            "status": "FAILED",
                            "message": "Certificate not issued by a trusted Indian CA",
                            "evaluation_mode": EVALUATION_MODE,
                        }
                    return {
                        "status": "FAILED",
                        "message": f"Digital signature is invalid or corrupt: {err_str}",
                        "evaluation_mode": EVALUATION_MODE,
                    }

                # Check signature integrity (tamper detection)
                if not val_status.intact:
                    return {
                        "status": "FAILED",
                        "message": "Digital signature is invalid or document has been modified after signing",
                        "evaluation_mode": EVALUATION_MODE,
                    }

                # Extract signer identity & signing time
                signing_cert = val_status.signing_cert
                signer_name = "Unknown Signer"
                if signing_cert:
                    try:
                        signer_name = (
                            signing_cert.subject.native.get("common_name")
                            or signing_cert.subject.human_friendly
                        )
                    except Exception:
                        signer_name = str(signing_cert.subject)

                signing_time = val_status.signer_reported_dt or signing_time

                # Extract certificate chain
                cert_chain = []
                if hasattr(val_status, "validation_path") and val_status.validation_path:
                    for c in val_status.validation_path:
                        cert_chain.append({
                            "subject": c.subject.human_friendly,
                            "issuer": c.issuer.human_friendly,
                        })

                # Validate certificate chain trust against Indian CCA root certificates
                if not getattr(val_status, "trusted", False):
                    return {
                        "status": "FAILED",
                        "message": "Certificate not issued by a trusted Indian CA",
                        "evaluation_mode": EVALUATION_MODE,
                        "signer_name": signer_name,
                        "signing_time": str(signing_time) if signing_time else None,
                        "certificate_chain": cert_chain,
                    }

                # Validate against trusted signers
                trusted_signers = get_trusted_signers()
                if trusted_signers:
                    is_trusted = any(
                        ts in signer_name.lower() or (signing_cert and ts in str(signing_cert.subject).lower())
                        for ts in trusted_signers
                    )
                    if not is_trusted:
                        return {
                            "status": "FAILED",
                            "message": f"Digital signature certificate signer '{signer_name}' is not in the trusted signers list",
                            "evaluation_mode": EVALUATION_MODE,
                            "signer_name": signer_name,
                            "signing_time": str(signing_time) if signing_time else None,
                            "certificate_chain": cert_chain,
                        }

        except Exception as e:
            return {
                "status": "FAILED",
                "message": f"Error parsing PDF digital signature: {str(e)}",
                "evaluation_mode": EVALUATION_MODE,
            }

        # 2. Extract text data with pdfplumber
        extracted = extract_certificate_data(file_path)

        # 3. Compare with student profile
        mismatch_reasons = []
        if student is not None:
            student_name = getattr(student, "name", None)
            extracted_name = extracted.get("name")

            if not student_name or not str(student_name).strip():
                mismatch_reasons.append("Student profile does not contain a name")
            elif not extracted_name or not str(extracted_name).strip():
                mismatch_reasons.append("Candidate name could not be extracted from certificate")
            else:
                ratio = fuzz.token_sort_ratio(str(extracted_name).lower().strip(), str(student_name).lower().strip())
                if ratio < 75.0:
                    mismatch_reasons.append(
                        f"Name on certificate '{extracted_name}' does not match profile '{student_name}'"
                    )

            # Date of Birth matching
            if extracted["date_of_birth"] and student.date_of_birth:
                if not check_dob_match(extracted["date_of_birth"], student.date_of_birth):
                    mismatch_reasons.append(
                        f"Date of birth on certificate '{extracted['date_of_birth']}' does not match profile '{student.date_of_birth}'"
                    )

            # Income matching for income certificates
            doc_type = getattr(document, "document_type", None)
            if doc_type == "INCOME_CERTIFICATE" and extracted["annual_family_income"] is not None and student.annual_family_income is not None:
                if extracted["annual_family_income"] != student.annual_family_income:
                    mismatch_reasons.append(
                        f"Income on certificate Rs {format_inr(extracted['annual_family_income'])} "
                        f"does not match profile Rs {format_inr(student.annual_family_income)}"
                    )

        # 4. Result outcome determination
        if mismatch_reasons:
            return {
                "status": "MISMATCH",
                "message": "; ".join(mismatch_reasons),
                "evaluation_mode": EVALUATION_MODE,
                "signer_name": signer_name,
                "signing_time": str(signing_time) if signing_time else None,
                "extracted_data": extracted,
                "certificate_chain": cert_chain,
            }

        return {
            "status": "VERIFIED",
            "message": f"Digitally signed document verified successfully. Signer: {signer_name}",
            "evaluation_mode": EVALUATION_MODE,
            "signer_name": signer_name,
            "signing_time": str(signing_time) if signing_time else None,
            "extracted_data": extracted,
            "certificate_chain": cert_chain,
        }
