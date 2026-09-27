from sqlalchemy.orm import Session
from app.models.application import Application
from app.schemas.application import ApplicationCreate
from app.repositories.application_repository import (
    create_application as repo_create_application,
    get_applications,
    get_application_by_id,
    update_application_status,
    create_application_status_history,
    get_application_status_history,
    get_student_by_id,
    get_scholarship_by_id,
)

ALLOWED_APPLICATION_STATUSES = {
    "DRAFT",
    "SUBMITTED",
    "IN_VERIFICATION",
    "DEFICIENCY",
    "SANCTIONED",
    "REJECTED",
    "WITHDRAWN",
    "COMPLETED",
}

ALLOWED_APPLICATION_TRANSITIONS = {
    "DRAFT": {"SUBMITTED", "WITHDRAWN"},
    "SUBMITTED": {"IN_VERIFICATION", "WITHDRAWN"},
    "IN_VERIFICATION": {"DEFICIENCY", "SANCTIONED", "REJECTED"},
    "DEFICIENCY": {"IN_VERIFICATION", "WITHDRAWN"},
    "SANCTIONED": {"COMPLETED"},
    "REJECTED": set(),
    "WITHDRAWN": set(),
    "COMPLETED": set(),
}


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


def transition_application_status(db: Session, application_id: str, target_status: str):
    # 1. Application exists
    application = get_application_by_id(db, application_id)
    if not application:
        return "APPLICATION_NOT_FOUND"

    # 2. Vocabulary validation
    if target_status not in ALLOWED_APPLICATION_STATUSES:
        return "INVALID_STATUS"

    # 3. Transition validation
    allowed_next = ALLOWED_APPLICATION_TRANSITIONS.get(application.status, set())
    if target_status not in allowed_next:
        return "INVALID_TRANSITION"

    # 4. Remember previous status
    old_status = application.status

    # 5. Atomic transaction: update application status + insert history row
    try:
        update_application_status(db, application, target_status, commit=False)
        create_application_status_history(
            db,
            application_id=application.id,
            from_status=old_status,
            to_status=target_status,
            commit=False,
        )
        db.commit()
        db.refresh(application)
        return application
    except Exception:
        db.rollback()
        raise


def get_application_timeline(db: Session, application_id: str):
    application = get_application_by_id(db, application_id)
    if not application:
        return "APPLICATION_NOT_FOUND"

    return get_application_status_history(db, application_id)
