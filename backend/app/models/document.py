from sqlalchemy import Column, String, ForeignKey
from app.core.database import Base
import uuid


class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    student_id = Column(String, ForeignKey("students.id"), nullable=False)
    document_type = Column(String, nullable=False)
    document_name = Column(String, nullable=False)
    status = Column(String, nullable=False, default="PENDING")
