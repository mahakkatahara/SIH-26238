import uuid
from sqlalchemy.orm import Session

from app.models.document import Document
from app.repositories.student_repository import get_student_by_id
from app.repositories.document_repository import (
    create_document,
    get_document_by_student_and_type,
)
from app.integrations.digilocker.mock_adapter import MockDigiLockerAdapter


def list_mock_digilocker_documents(db: Session, student_id: str):
    # 1. Validate Student exists
    student = get_student_by_id(db, student_id)
    if not student:
        return "STUDENT_NOT_FOUND"

    # 2. Invoke mock adapter
    return MockDigiLockerAdapter.list_documents(student)


def import_mock_digilocker_document(db: Session, student_id: str, document_type: str):
    # 1. Validate Student exists
    student = get_student_by_id(db, student_id)
    if not student:
        return "STUDENT_NOT_FOUND"

    # 2. Invoke mock catalogue
    catalogue = MockDigiLockerAdapter.list_documents(student)

    # 3. Find requested document_type
    matched_doc = next((d for d in catalogue if d["document_type"] == document_type), None)
    if not matched_doc:
        return "MOCK_DOCUMENT_NOT_FOUND"

    # 4. Check whether same student already has same mock document_type
    existing = get_document_by_student_and_type(db, student_id, document_type)
    if existing:
        return "MOCK_DOCUMENT_ALREADY_IMPORTED"

    # 5. Create ordinary Document
    new_doc = Document(
        id=str(uuid.uuid4()),
        student_id=student_id,
        document_type=matched_doc["document_type"],
        document_name=matched_doc["document_name"],
        source="DIGILOCKER_MOCK",
        status="PENDING",
    )
    return create_document(db, new_doc)
