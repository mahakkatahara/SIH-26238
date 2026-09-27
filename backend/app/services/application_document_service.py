from sqlalchemy.orm import Session
from app.models.application_document import ApplicationDocument
from app.repositories.application_repository import get_application_by_id
from app.repositories.document_repository import get_document_by_id
from app.repositories.application_document_repository import (
    get_application_document,
    create_application_document as repo_create_application_document,
    get_documents_by_application_id,
)


def link_document_to_application(db: Session, application_id: str, document_id: str):
    application = get_application_by_id(db, application_id)
    if not application:
        return "APPLICATION_NOT_FOUND"

    document = get_document_by_id(db, document_id)
    if not document:
        return "DOCUMENT_NOT_FOUND"

    if document.student_id != application.student_id:
        return "STUDENT_MISMATCH"

    existing_link = get_application_document(db, application_id, document_id)
    if existing_link:
        return "ALREADY_LINKED"

    new_link = ApplicationDocument(
        application_id=application_id,
        document_id=document_id,
    )
    return repo_create_application_document(db, new_link)


def get_application_documents(db: Session, application_id: str):
    application = get_application_by_id(db, application_id)
    if not application:
        return "APPLICATION_NOT_FOUND"

    return get_documents_by_application_id(db, application_id)
