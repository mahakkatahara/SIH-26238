import uuid
from sqlalchemy.orm import Session
from app.models.manual_review import ManualReview


def get_manual_review_by_verification_id(db: Session, verification_id: str):
    return (
        db.query(ManualReview)
        .filter(ManualReview.verification_id == verification_id)
        .first()
    )


def create_manual_review(db: Session, application_id: str, verification_id: str, commit: bool = True):
    review = ManualReview(
        id=str(uuid.uuid4()),
        application_id=application_id,
        verification_id=verification_id,
        status="OPEN",
    )
    db.add(review)
    if commit:
        db.commit()
        db.refresh(review)
    return review


def get_manual_reviews(db: Session):
    return db.query(ManualReview).all()
