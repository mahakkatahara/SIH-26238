from sqlalchemy.orm import Session
from app.repositories.scholarship_repository import get_scholarships


def list_scholarships(db: Session):
    return get_scholarships(db)
