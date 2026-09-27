import uuid
from sqlalchemy import Column, String, ForeignKey, UniqueConstraint
from app.core.database import Base


class Payment(Base):
    __tablename__ = "payments"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    application_id = Column(String, ForeignKey("applications.id"), nullable=False)
    status = Column(String, nullable=False, default="SANCTIONED")

    __table_args__ = (
        UniqueConstraint("application_id", name="uq_application_payment"),
    )
