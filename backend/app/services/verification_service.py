from sqlalchemy.orm import Session
from app.repositories.application_repository import get_application_by_id
from app.repositories.document_repository import get_document_by_id
from app.repositories.student_repository import get_student_by_id
from app.repositories.application_document_repository import get_application_document
from app.repositories.verification_repository import (
    get_verification_record,
    create_verification_record as repo_create_verification_record,
    get_verifications_by_application_id,
    get_verification_by_id,
    update_verification_status,
)
from app.repositories.manual_review_repository import (
    get_manual_review_by_verification_id,
    create_manual_review as repo_create_manual_review,
)
from app.integrations.verification.mock_adapter import MockVerificationAdapter
from app.integrations.verification.signed_pdf_adapter import SignedPdfVerificationAdapter


def create_verification_record(db: Session, application_id: str, document_id: str):
    # 1. Validate application exists
    application = get_application_by_id(db, application_id)
    if not application:
        return "APPLICATION_NOT_FOUND"

    # 2. Validate document exists
    document = get_document_by_id(db, document_id)
    if not document:
        return "DOCUMENT_NOT_FOUND"

    # 3. Validate application_documents link exists
    link = get_application_document(db, application_id, document_id)
    if not link:
        return "DOCUMENT_NOT_LINKED"

    # 4. Validate duplicate verification does not exist
    existing = get_verification_record(db, application_id, document_id)
    if existing:
        return "VERIFICATION_ALREADY_EXISTS"

    # 5 & 6. Create record with UUID and status PENDING
    return repo_create_verification_record(db, application_id, document_id)


def get_application_verifications(db: Session, application_id: str):
    # 1. Validate application exists
    application = get_application_by_id(db, application_id)
    if not application:
        return "APPLICATION_NOT_FOUND"

    # 2. Retrieve records
    return get_verifications_by_application_id(db, application_id)


def execute_verification(db: Session, verification_id: str):
    # 1. Find verification record
    verification = get_verification_by_id(db, verification_id)
    if not verification:
        return "VERIFICATION_NOT_FOUND"

    # 2. Verify status is PENDING
    if verification.status != "PENDING":
        return "NOT_PENDING"

    # 3. Load associated document
    document = get_document_by_id(db, verification.document_id)
    if not document:
        return "DOCUMENT_NOT_FOUND"

    # 4. Invoke appropriate adapter
    doc_source = getattr(document, "source", None)
    if doc_source == "PDF_UPLOAD":
        application = get_application_by_id(db, verification.application_id)
        student = get_student_by_id(db, application.student_id) if application else None
        if not student or not getattr(student, "name", None) or not str(student.name).strip():
            result = {
                "status": "MISMATCH",
                "message": "Student profile has no name or student record is missing",
                "evaluation_mode": "SIGNED_PDF",
            }
        else:
            result = SignedPdfVerificationAdapter.verify_document(document, student=student)
    else:
        result = MockVerificationAdapter.verify_document(document)

    # 5. Persist status update
    update_verification_status(db, verification, result["status"])

    # If verification status is MISMATCH, route to manual review exception queue
    if result["status"] == "MISMATCH":
        existing_review = get_manual_review_by_verification_id(db, verification.id)
        if not existing_review:
            repo_create_manual_review(db, verification.application_id, verification.id)

    # 6. Return execution response payload
    return {
        "id": verification.id,
        "application_id": verification.application_id,
        "document_id": verification.document_id,
        "status": verification.status,
        "message": result["message"],
        "evaluation_mode": result["evaluation_mode"],
    }
