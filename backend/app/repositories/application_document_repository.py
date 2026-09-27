from sqlalchemy.orm import Session
from app.models.application_document import ApplicationDocument
from app.models.document import Document


def get_application_document(db: Session, application_id: str, document_id: str):
    return (
        db.query(ApplicationDocument)
        .filter(
            ApplicationDocument.application_id == application_id,
            ApplicationDocument.document_id == document_id,
        )
        .first()
    )


def create_application_document(db: Session, application_document: ApplicationDocument):
    db.add(application_document)
    db.commit()
    db.refresh(application_document)
    return application_document


def get_documents_by_application_id(db: Session, application_id: str):
    return (
        db.query(Document)
        .join(ApplicationDocument, Document.id == ApplicationDocument.document_id)
        .filter(ApplicationDocument.application_id == application_id)
        .all()
    )
