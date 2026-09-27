from sqlalchemy.orm import Session
from app.models.scholarship import Scholarship


def get_scholarships(db: Session):
    return db.query(Scholarship).all()


def get_scholarship_by_id(db: Session, scholarship_id: str):
    return db.query(Scholarship).filter(Scholarship.id == scholarship_id).first()
