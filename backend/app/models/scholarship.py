import uuid
from sqlalchemy import Boolean, Column, Integer, JSON, String
from app.core.database import Base


class Scholarship(Base):
    __tablename__ = "scholarships"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    code = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)

    scheme_type = Column(String, nullable=True)
    income_ceiling = Column(Integer, nullable=True)
    eligible_levels = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
