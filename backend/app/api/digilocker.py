from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.schemas.digilocker import MockDigiLockerDocument, MockDigiLockerImportRequest
from app.schemas.document import DocumentResponse
from app.services.digilocker_service import (
    list_mock_digilocker_documents,
    import_mock_digilocker_document,
)

router = APIRouter(tags=["DigiLocker"])


@router.get(
    "/students/{student_id}/digilocker/documents",
    response_model=list[MockDigiLockerDocument],
)
@router.get(
    "/students/{student_id}/digilocker/documents/",
    response_model=list[MockDigiLockerDocument],
    include_in_schema=False,
)
def list_digilocker_documents_api(
    student_id: str,
    db: Session = Depends(get_db),
):
    result = list_mock_digilocker_documents(db, student_id)

    if result == "STUDENT_NOT_FOUND":
        raise HTTPException(
            status_code=404,
            detail="Student not found",
        )

    return result


@router.post(
    "/students/{student_id}/digilocker/documents/import",
    response_model=DocumentResponse,
)
@router.post(
    "/students/{student_id}/digilocker/documents/import/",
    response_model=DocumentResponse,
    include_in_schema=False,
)
def import_digilocker_document_api(
    student_id: str,
    payload: MockDigiLockerImportRequest,
    db: Session = Depends(get_db),
):
    result = import_mock_digilocker_document(db, student_id, payload.document_type)

    if result == "STUDENT_NOT_FOUND":
        raise HTTPException(
            status_code=404,
            detail="Student not found",
        )

    if result == "MOCK_DOCUMENT_NOT_FOUND":
        raise HTTPException(
            status_code=404,
            detail="Mock DigiLocker document not found",
        )

    if result == "MOCK_DOCUMENT_ALREADY_IMPORTED":
        raise HTTPException(
            status_code=409,
            detail="Mock DigiLocker document already imported",
        )

    return result
