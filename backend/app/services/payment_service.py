from sqlalchemy.orm import Session
from app.repositories.application_repository import get_application_by_id
from app.repositories.payment_repository import (
    get_payment_by_id,
    get_payment_by_application_id,
    get_payments_by_application_id,
    create_payment as repo_create_payment,
    update_payment_status,
)

ALLOWED_PAYMENT_STATUSES = {
    "SANCTIONED",
    "DBT_INITIATED",
    "PROCESSING",
    "CREDITED",
    "FAILED",
}

ALLOWED_PAYMENT_TRANSITIONS = {
    "SANCTIONED": {"DBT_INITIATED"},
    "DBT_INITIATED": {"PROCESSING"},
    "PROCESSING": {"CREDITED", "FAILED"},
    "CREDITED": set(),
    "FAILED": set(),
}


def create_payment(db: Session, application_id: str):
    # 1. Validate Application exists
    application = get_application_by_id(db, application_id)
    if not application:
        return "APPLICATION_NOT_FOUND"

    # 2. Validate Application is SANCTIONED
    if application.status != "SANCTIONED":
        return "APPLICATION_NOT_SANCTIONED"

    # 3. Check duplicate Payment
    existing = get_payment_by_application_id(db, application_id)
    if existing:
        return "PAYMENT_ALREADY_EXISTS"

    # 4. Create Payment with initial status SANCTIONED
    return repo_create_payment(db, application_id, status="SANCTIONED")


def get_application_payments(db: Session, application_id: str):
    # 1. Validate Application exists
    application = get_application_by_id(db, application_id)
    if not application:
        return "APPLICATION_NOT_FOUND"

    # 2. Return payments list
    return get_payments_by_application_id(db, application_id)


def transition_payment_status(db: Session, payment_id: str, target_status: str):
    # 1. Validate Payment exists
    payment = get_payment_by_id(db, payment_id)
    if not payment:
        return "PAYMENT_NOT_FOUND"

    # 2. Validate requested status belongs to exact Playbook vocabulary
    if target_status not in ALLOWED_PAYMENT_STATUSES:
        return "INVALID_STATUS"

    # 3. Validate transition against explicit map
    allowed_next = ALLOWED_PAYMENT_TRANSITIONS.get(payment.status, set())
    if target_status not in allowed_next:
        return "INVALID_TRANSITION"

    # 4. Persist updated status
    return update_payment_status(db, payment, target_status)
