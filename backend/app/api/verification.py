from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.schemas.verification import (
    VerificationCreate,
    VerificationRecordResponse,
    VerificationExecutionResponse,
)
from app.services.verification_service import (
    create_verification_record,
    get_application_verifications,
    execute_verification,
)

router = APIRouter(tags=["Verification"])


@router.post("/applications/{application_id}/verifications", response_model=VerificationRecordResponse)
@router.post("/applications/{application_id}/verifications/", response_model=VerificationRecordResponse, include_in_schema=False)
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


@router.get("/applications/{application_id}/verifications", response_model=list[VerificationRecordResponse])
@router.get("/applications/{application_id}/verifications/", response_model=list[VerificationRecordResponse], include_in_schema=False)
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


@router.post("/verifications/{verification_id}/execute", response_model=VerificationExecutionResponse)
@router.post("/verifications/{verification_id}/execute/", response_model=VerificationExecutionResponse, include_in_schema=False)
def execute_verification_api(
    verification_id: str,
    db: Session = Depends(get_db)
):
    result = execute_verification(db, verification_id)

    if result == "VERIFICATION_NOT_FOUND":
        raise HTTPException(
            status_code=404,
            detail="Verification record not found"
        )

    if result == "NOT_PENDING":
        raise HTTPException(
            status_code=409,
            detail="Verification record is not pending"
        )

    if result == "DOCUMENT_NOT_FOUND":
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    return result
