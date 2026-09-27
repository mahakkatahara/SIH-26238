from sqlalchemy.orm import Session
from app.models.verification_record import VerificationRecord


def get_verification_record(db: Session, application_id: str, document_id: str):
    return (
        db.query(VerificationRecord)
        .filter(
            VerificationRecord.application_id == application_id,
            VerificationRecord.document_id == document_id,
        )
        .first()
    )


def create_verification_record(db: Session, application_id: str, document_id: str):
    record = VerificationRecord(
        application_id=application_id,
        document_id=document_id,
        status="PENDING",
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_verifications_by_application_id(db: Session, application_id: str):
    return (
        db.query(VerificationRecord)
        .filter(VerificationRecord.application_id == application_id)
        .all()
    )


def get_verification_by_id(db: Session, verification_id: str):
    return (
        db.query(VerificationRecord)
        .filter(VerificationRecord.id == verification_id)
        .first()
    )


def update_verification_status(db: Session, verification: VerificationRecord, status: str):
    verification.status = status
    db.commit()
    db.refresh(verification)
    return verification
