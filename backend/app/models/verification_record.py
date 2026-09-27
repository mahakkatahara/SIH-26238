from sqlalchemy import Column, String, ForeignKey, UniqueConstraint
from app.core.database import Base
import uuid


class VerificationRecord(Base):
    __tablename__ = "verification_records"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    application_id = Column(String, ForeignKey("applications.id"), nullable=False)
    document_id = Column(String, ForeignKey("documents.id"), nullable=False)
    status = Column(String, nullable=False, default="PENDING")

    __table_args__ = (
        UniqueConstraint("application_id", "document_id", name="uq_application_document_verification"),
    )
