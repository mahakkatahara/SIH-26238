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


import uuid
from app.models.application_status_history import ApplicationStatusHistory


def get_application_by_id(db: Session, application_id: str):
    return db.query(Application).filter(Application.id == application_id).first()


def update_application_status(db: Session, application: Application, status: str, commit: bool = True):
    application.status = status
    if commit:
        db.commit()
        db.refresh(application)
    return application


def create_application_status_history(
    db: Session,
    application_id: str,
    from_status: str,
    to_status: str,
    commit: bool = True
):
    history = ApplicationStatusHistory(
        id=str(uuid.uuid4()),
        application_id=application_id,
        from_status=from_status,
        to_status=to_status,
    )
    db.add(history)
    if commit:
        db.commit()
        db.refresh(history)
    return history


def get_application_status_history(db: Session, application_id: str):
    return (
        db.query(ApplicationStatusHistory)
        .filter(ApplicationStatusHistory.application_id == application_id)
        .all()
    )
