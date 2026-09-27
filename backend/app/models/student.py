import uuid
from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.core.database import Base


class Student(Base):
    __tablename__ = "students"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    user_id = Column(String, ForeignKey("users.id"), unique=True, nullable=True)

    tribe_status = Column(String, nullable=True)
    state = Column(String, nullable=True)
    annual_family_income = Column(Integer, nullable=True)
    education_level = Column(String, nullable=True)
    institution_name = Column(String, nullable=True)
    is_hosteller = Column(Boolean, nullable=True)
    date_of_birth = Column(Date, nullable=True)
    study_country = Column(String, nullable=True)

    user = relationship("User", back_populates="student")