import argparse
import sys
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.core.security import hash_password
from app.models.user import User
from app.models.student import Student
from app.models.scholarship import Scholarship
from app.models.application import Application
from app.models.document import Document
from app.models.application_document import ApplicationDocument
from app.models.verification_record import VerificationRecord
from app.models.manual_review import ManualReview

# Deterministic Demo IDs (UUID v4 format)
DEMO_USER_ID = "00000000-0000-0000-0000-000000000001"
DEMO_STUDENT_ID = "00000000-0000-0000-0000-000000000002"

DEMO_SCHOLARSHIPS = [
    {
        "id": "00000000-0000-0000-0000-000000000010",
        "code": "POST_MATRIC",
        "name": "Post-Matric Scholarship",
    },
    {
        "id": "00000000-0000-0000-0000-000000000011",
        "code": "PRE_MATRIC",
        "name": "Pre-Matric Scholarship",
    },
    {
        "id": "00000000-0000-0000-0000-000000000012",
        "code": "NATIONAL_OVERSEAS",
        "name": "National Overseas Scholarship",
    },
    {
        "id": "00000000-0000-0000-0000-000000000013",
        "code": "TOP_CLASS_EDUCATION",
        "name": "National Fellowship and Scholarship for Higher Education of ST Students",
    },
]

DEMO_APPLICATION_ID = "00000000-0000-0000-0000-000000000020"

DEMO_DOCUMENTS = [
    {
        "id": "00000000-0000-0000-0000-000000000030",
        "student_id": DEMO_STUDENT_ID,
        "document_type": "MOCK_ST_CERTIFICATE",
        "document_name": "ST Certificate",
        "status": "PENDING",
    },
    {
        "id": "00000000-0000-0000-0000-000000000031",
        "student_id": DEMO_STUDENT_ID,
        "document_type": "TEST_VERIFIED",
        "document_name": "Verified Marksheet",
        "status": "PENDING",
    },
    {
        "id": "00000000-0000-0000-0000-000000000032",
        "student_id": DEMO_STUDENT_ID,
        "document_type": "TEST_MISMATCH",
        "document_name": "Income Certificate Demo",
        "status": "PENDING",
    },
]

DEMO_VERIFICATION_ID = "00000000-0000-0000-0000-000000000040"


def seed_database(db: Session, reset: bool = False) -> dict:
    """Idempotently seed deterministic demo/synthetic data for frontend and local integration.
    
    If reset=True, previously seeded demo records will be deleted first.
    """
    if reset:
        # Delete child records first in dependency order
        db.query(ManualReview).filter(ManualReview.id.like("00000000-0000-0000-0000-%")).delete(synchronize_session=False)
        db.query(VerificationRecord).filter(VerificationRecord.id.like("00000000-0000-0000-0000-%")).delete(synchronize_session=False)
        db.query(ApplicationDocument).filter(ApplicationDocument.application_id == DEMO_APPLICATION_ID).delete(synchronize_session=False)
        db.query(Application).filter(Application.id.like("00000000-0000-0000-0000-%")).delete(synchronize_session=False)
        db.query(Document).filter(Document.id.like("00000000-0000-0000-0000-%")).delete(synchronize_session=False)
        for s in DEMO_SCHOLARSHIPS:
            db.query(Scholarship).filter(Scholarship.code == s["code"]).delete(synchronize_session=False)
        db.query(Student).filter(Student.id == DEMO_STUDENT_ID).delete(synchronize_session=False)
        db.query(User).filter(User.id == DEMO_USER_ID).delete(synchronize_session=False)
        db.commit()

    created_counts = {
        "users": 0,
        "students": 0,
        "scholarships": 0,
        "applications": 0,
        "documents": 0,
        "application_documents": 0,
        "verification_records": 0,
    }

    # 1. User
    user = db.query(User).filter(User.id == DEMO_USER_ID).first()
    if not user:
        user_by_email = db.query(User).filter(User.email == "demo.student@example.com").first()
        if not user_by_email:
            user = User(
                id=DEMO_USER_ID,
                name="Demo Student User",
                email="demo.student@example.com",
                password=hash_password("DemoPassword123!"),
            )
            db.add(user)
            db.flush()
            created_counts["users"] += 1
        else:
            user = user_by_email

    # 2. Student
    student = db.query(Student).filter(Student.id == DEMO_STUDENT_ID).first()
    if not student:
        student_by_email = db.query(Student).filter(Student.email == "demo.student@example.com").first()
        if not student_by_email:
            student = Student(
                id=DEMO_STUDENT_ID,
                user_id=user.id,
                name="Demo Student User",
                email="demo.student@example.com",
            )
            db.add(student)
            db.flush()
            created_counts["students"] += 1
        else:
            student = student_by_email

    # 3. Scholarships
    for s_data in DEMO_SCHOLARSHIPS:
        existing = db.query(Scholarship).filter(Scholarship.code == s_data["code"]).first()
        if not existing:
            scholarship = Scholarship(
                id=s_data["id"],
                code=s_data["code"],
                name=s_data["name"],
            )
            db.add(scholarship)
            db.flush()
            created_counts["scholarships"] += 1

    # 4. Application
    app = db.query(Application).filter(Application.id == DEMO_APPLICATION_ID).first()
    if not app:
        app = Application(
            id=DEMO_APPLICATION_ID,
            student_id=student.id,
            scholarship_id=DEMO_SCHOLARSHIPS[0]["id"],
            status="DRAFT",
        )
        db.add(app)
        db.flush()
        created_counts["applications"] += 1

    # 5. Documents
    for d_data in DEMO_DOCUMENTS:
        doc = db.query(Document).filter(Document.id == d_data["id"]).first()
        if not doc:
            doc = Document(
                id=d_data["id"],
                student_id=student.id,
                document_type=d_data["document_type"],
                document_name=d_data["document_name"],
                status=d_data["status"],
            )
            db.add(doc)
            db.flush()
            created_counts["documents"] += 1

    # 6. Application Documents Link
    for d_data in DEMO_DOCUMENTS[:2]:
        link = (
            db.query(ApplicationDocument)
            .filter(
                ApplicationDocument.application_id == DEMO_APPLICATION_ID,
                ApplicationDocument.document_id == d_data["id"],
            )
            .first()
        )
        if not link:
            link = ApplicationDocument(
                application_id=DEMO_APPLICATION_ID,
                document_id=d_data["id"],
            )
            db.add(link)
            db.flush()
            created_counts["application_documents"] += 1

    # 7. Verification Record
    verif = (
        db.query(VerificationRecord)
        .filter(VerificationRecord.id == DEMO_VERIFICATION_ID)
        .first()
    )
    if not verif:
        verif = VerificationRecord(
            id=DEMO_VERIFICATION_ID,
            application_id=DEMO_APPLICATION_ID,
            document_id=DEMO_DOCUMENTS[0]["id"],
            status="PENDING",
        )
        db.add(verif)
        db.flush()
        created_counts["verification_records"] += 1

    db.commit()
    return created_counts


def main():
    parser = argparse.ArgumentParser(description="Seed database with synthetic demo data")
    parser.add_argument("--reset", action="store_true", help="Reset existing seeded demo records")
    args = parser.parse_args()

    db = SessionLocal()
    try:
        results = seed_database(db, reset=args.reset)
        print("Database seeded successfully:")
        for model_name, count in results.items():
            print(f"  - {model_name}: {count} new record(s)")
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
