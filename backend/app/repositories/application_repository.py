from sqlalchemy.orm import Session
from app.models.application import Application
from app.repositories.student_repository import get_student_by_id
from app.repositories.scholarship_repository import get_scholarship_by_id


def create_application(db: Session, application: Application):
    db.add(application)
    db.commit()
    db.refresh(application)
    return application


def get_applications(db: Session):
    return db.query(Application).all()


def get_application_by_id(db: Session, application_id: str):
    return db.query(Application).filter(Application.id == application_id).first()
