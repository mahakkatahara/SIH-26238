from sqlalchemy.orm import Session
from app.models.application import Application
from app.schemas.application import ApplicationCreate
from app.repositories.application_repository import (
    create_application as repo_create_application,
    get_applications,
    get_student_by_id,
    get_scholarship_by_id
)


def create_application(db: Session, application: ApplicationCreate):
    student = get_student_by_id(db, application.student_id)
    if not student:
        return "STUDENT_NOT_FOUND"

    scholarship = get_scholarship_by_id(db, application.scholarship_id)
    if not scholarship:
        return "SCHOLARSHIP_NOT_FOUND"

    new_application = Application(
        student_id=application.student_id,
        scholarship_id=application.scholarship_id,
        status="DRAFT"
    )

    return repo_create_application(db, new_application)


def list_applications(db: Session):
    return get_applications(db)
