from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.schemas.application import ApplicationCreate, ApplicationResponse
from app.services.application_service import create_application, list_applications

router = APIRouter(prefix="/applications", tags=["Applications"])


@router.post("", response_model=ApplicationResponse)
@router.post("/", response_model=ApplicationResponse, include_in_schema=False)
def create_application_api(
    application: ApplicationCreate,
    db: Session = Depends(get_db)
):
    result = create_application(db, application)

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


@router.get("", response_model=list[ApplicationResponse])
@router.get("/", response_model=list[ApplicationResponse], include_in_schema=False)
def list_applications_api(db: Session = Depends(get_db)):
    return list_applications(db)
