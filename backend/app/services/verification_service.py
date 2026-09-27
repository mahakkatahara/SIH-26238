from sqlalchemy.orm import Session
from app.repositories.application_repository import get_application_by_id
from app.repositories.document_repository import get_document_by_id
from app.repositories.application_document_repository import get_application_document
from app.repositories.verification_repository import (
    get_verification_record,
    create_verification_record as repo_create_verification_record,
    get_verifications_by_application_id,
    get_verification_by_id,
    update_verification_status,
)
from app.integrations.verification.mock_adapter import MockVerificationAdapter


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

    # 4. Invoke mock adapter
    mock_result = MockVerificationAdapter.verify_document(document)

    # 5. Persist only status update
    update_verification_status(db, verification, mock_result["status"])

    # 6. Return execution response payload
    return {
        "id": verification.id,
        "application_id": verification.application_id,
        "document_id": verification.document_id,
        "status": verification.status,
        "message": mock_result["message"],
        "evaluation_mode": mock_result["evaluation_mode"],
    }
