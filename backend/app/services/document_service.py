from sqlalchemy.orm import Session
from app.models.document import Document
from app.schemas.document import DocumentCreate
from app.repositories.document_repository import (
    create_document as repo_create_document,
    get_documents,
)
from app.repositories.student_repository import get_student_by_id


def create_document(db: Session, document: DocumentCreate):
    student = get_student_by_id(db, document.student_id)
    if not student:
        return "STUDENT_NOT_FOUND"

    new_document = Document(
        student_id=document.student_id,
        document_type=document.document_type,
        document_name=document.document_name,
        file_path=document.file_path,
        source=document.source,
        status="PENDING"
    )

    return repo_create_document(db, new_document)


def upload_student_document(
    db: Session,
    student_id: str,
    document_type: str,
    filename: str,
    file_path: str,
):
    student = get_student_by_id(db, student_id)
    if not student:
        return "STUDENT_NOT_FOUND"

    new_document = Document(
        student_id=student_id,
        document_type=document_type,
        document_name=filename,
        file_path=file_path,
        source="PDF_UPLOAD",
        status="PENDING",
    )

    return repo_create_document(db, new_document)


def list_documents(db: Session):
    return get_documents(db)
