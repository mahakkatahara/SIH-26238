from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.schemas.manual_review import ManualReviewResponse
from app.services.manual_review_service import (
    create_manual_review,
    get_manual_reviews,
)

router = APIRouter(tags=["Manual Review"])


@router.post(
    "/verifications/{verification_id}/manual-review",
    response_model=ManualReviewResponse,
)
@router.post(
    "/verifications/{verification_id}/manual-review/",
    response_model=ManualReviewResponse,
    include_in_schema=False,
)
def create_manual_review_api(
    verification_id: str,
    db: Session = Depends(get_db),
):
    result = create_manual_review(db, verification_id)

    if result == "VERIFICATION_NOT_FOUND":
        raise HTTPException(
            status_code=404,
            detail="Verification record not found",
        )

    if result == "NOT_ELIGIBLE":
        raise HTTPException(
            status_code=409,
            detail="Verification record is not eligible for manual review",
        )

    if result == "REVIEW_ALREADY_EXISTS":
        raise HTTPException(
            status_code=409,
            detail="Manual review already exists",
        )

    return result


@router.get(
    "/manual-reviews",
    response_model=list[ManualReviewResponse],
)
@router.get(
    "/manual-reviews/",
    response_model=list[ManualReviewResponse],
    include_in_schema=False,
)
def list_manual_reviews_api(
    db: Session = Depends(get_db),
):
    return get_manual_reviews(db)
