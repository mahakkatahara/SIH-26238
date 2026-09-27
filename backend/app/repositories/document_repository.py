from sqlalchemy.orm import Session
from app.models.document import Document


def create_document(db: Session, document: Document):
    db.add(document)
    db.commit()
    db.refresh(document)
    return document


def get_documents(db: Session):
    return db.query(Document).all()


def get_document_by_id(db: Session, document_id: str):
    return db.query(Document).filter(Document.id == document_id).first()
