from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.schemas.eligibility import EligibilityCheckRequest, EligibilityCheckResponse
from app.services.eligibility_service import check_eligibility

router = APIRouter(prefix="/eligibility", tags=["Eligibility"])


@router.post("/check", response_model=EligibilityCheckResponse)
@router.post("/check/", response_model=EligibilityCheckResponse, include_in_schema=False)
def check_eligibility_api(
    payload: EligibilityCheckRequest,
    db: Session = Depends(get_db)
):
    result = check_eligibility(db, payload)

    if result == "STUDENT_NOT_FOUND":
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    if result == "SCHOLARSHIP_NOT_FOUND":
        raise HTTPException(
            status_code=404,
            detail="Scholarship not found"
        )

    return result
