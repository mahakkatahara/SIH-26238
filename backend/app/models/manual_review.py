from sqlalchemy import Column, String, ForeignKey, UniqueConstraint
from app.core.database import Base
import uuid


class ManualReview(Base):
    __tablename__ = "manual_reviews"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    application_id = Column(String, ForeignKey("applications.id"), nullable=False)
    verification_id = Column(String, ForeignKey("verification_records.id"), nullable=False)
    status = Column(String, nullable=False, default="OPEN")

    __table_args__ = (
        UniqueConstraint("verification_id", name="uq_manual_review_verification"),
    )
