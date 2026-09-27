from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.schemas.verification import VerificationCreate, VerificationRecordResponse
from app.services.verification_service import (
    create_verification_record,
    get_application_verifications,
)

router = APIRouter(prefix="/applications", tags=["Verification"])


@router.post("/{application_id}/verifications", response_model=VerificationRecordResponse)
@router.post("/{application_id}/verifications/", response_model=VerificationRecordResponse, include_in_schema=False)
def create_verification_api(
    application_id: str,
    payload: VerificationCreate,
    db: Session = Depends(get_db)
):
    result = create_verification_record(db, application_id, payload.document_id)

    if result == "APPLICATION_NOT_FOUND":
        raise HTTPException(
            status_code=404,
            detail="Application not found"
        )

    if result == "DOCUMENT_NOT_FOUND":
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    if result == "DOCUMENT_NOT_LINKED":
        raise HTTPException(
            status_code=409,
            detail="Document is not linked to application"
        )

    if result == "VERIFICATION_ALREADY_EXISTS":
        raise HTTPException(
            status_code=409,
            detail="Verification record already exists"
        )

    return result


@router.get("/{application_id}/verifications", response_model=list[VerificationRecordResponse])
@router.get("/{application_id}/verifications/", response_model=list[VerificationRecordResponse], include_in_schema=False)
def list_application_verifications_api(
    application_id: str,
    db: Session = Depends(get_db)
):
    result = get_application_verifications(db, application_id)

    if result == "APPLICATION_NOT_FOUND":
        raise HTTPException(
            status_code=404,
            detail="Application not found"
        )

    return result
