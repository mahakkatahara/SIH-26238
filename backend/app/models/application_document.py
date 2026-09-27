from sqlalchemy import Column, String, ForeignKey
from app.core.database import Base


class ApplicationDocument(Base):
    __tablename__ = "application_documents"

    application_id = Column(String, ForeignKey("applications.id"), primary_key=True, nullable=False)
    document_id = Column(String, ForeignKey("documents.id"), primary_key=True, nullable=False)
