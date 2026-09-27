import uuid
from sqlalchemy.orm import Session
from app.models.payment import Payment


def get_payment_by_id(db: Session, payment_id: str):
    return db.query(Payment).filter(Payment.id == payment_id).first()


def get_payment_by_application_id(db: Session, application_id: str):
    return db.query(Payment).filter(Payment.application_id == application_id).first()


def get_payments_by_application_id(db: Session, application_id: str):
    return db.query(Payment).filter(Payment.application_id == application_id).all()


def create_payment(db: Session, application_id: str, status: str = "SANCTIONED", commit: bool = True):
    payment = Payment(
        id=str(uuid.uuid4()),
        application_id=application_id,
        status=status,
    )
    db.add(payment)
    if commit:
        db.commit()
        db.refresh(payment)
    return payment


def update_payment_status(db: Session, payment: Payment, status: str, commit: bool = True):
    payment.status = status
    if commit:
        db.commit()
        db.refresh(payment)
    return payment
