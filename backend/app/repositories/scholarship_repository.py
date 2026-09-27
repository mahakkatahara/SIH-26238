from sqlalchemy.orm import Session
from app.models.scholarship import Scholarship


def get_scholarships(db: Session):
    return db.query(Scholarship).all()
