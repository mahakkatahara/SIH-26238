import uuid
from sqlalchemy import Column, String, ForeignKey
from app.core.database import Base


class ApplicationStatusHistory(Base):
    __tablename__ = "application_status_history"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    application_id = Column(String, ForeignKey("applications.id"), nullable=False)
    from_status = Column(String, nullable=False)
    to_status = Column(String, nullable=False)
