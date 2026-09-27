import uuid
from sqlalchemy import Column, ForeignKey, String
from app.core.database import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    student_id = Column(String, ForeignKey("students.id"), nullable=False)
    document_type = Column(String, nullable=False)
    document_name = Column(String, nullable=False)
    file_path = Column(String, nullable=True)
    source = Column(String, nullable=True, default=None)
    status = Column(String, nullable=False, default="PENDING")
