import uuid
from pathlib import Path
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.schemas.document import DocumentResponse
from app.schemas.eligibility import EligibilityCheckResponse
from app.schemas.student import StudentCreate, StudentResponse, StudentUpdate
from app.services.document_service import upload_student_document
from app.services.eligibility_service import evaluate_student_for_all_schemes
from app.services.student_service import (
    add_student,
    get_student,
    list_students,
    update_student_profile,
)

router = APIRouter(prefix="/students", tags=["Students"])

UPLOAD_DIR = Path(__file__).resolve().parent.parent.parent / "uploads"
ALLOWED_DOCUMENT_TYPES = {
    "ST_CERTIFICATE",
    "INCOME_CERTIFICATE",
    "CLASS_12_MARKSHEET",
    "DOMICILE_CERTIFICATE",
}
MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB


@router.post("", response_model=StudentResponse)
@router.post("/", response_model=StudentResponse, include_in_schema=False)
def add_student_api(student: StudentCreate, db: Session = Depends(get_db)):
    result = add_student(db, student)

    if result == "USER_NOT_FOUND":
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if result == "STUDENT_ALREADY_EXISTS":
        raise HTTPException(
            status_code=409,
            detail="Student profile already exists for this user"
        )

    if result == "EMAIL_ALREADY_EXISTS":
        raise HTTPException(
            status_code=409,
            detail="Email already registered for another student"
        )

    return result


@router.get("", response_model=list[StudentResponse])
@router.get("/", response_model=list[StudentResponse], include_in_schema=False)
def list_students_api(db: Session = Depends(get_db)):
    return list_students(db)


@router.get("/{student_id}", response_model=StudentResponse)
def get_student_api(student_id: str, db: Session = Depends(get_db)):
    student = get_student(db, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


@router.patch("/{student_id}", response_model=StudentResponse)
@router.put("/{student_id}", response_model=StudentResponse)
def update_student_api(
    student_id: str,
    payload: StudentUpdate,
    db: Session = Depends(get_db)
):
    result = update_student_profile(db, student_id, payload)
    if result is None:
        raise HTTPException(status_code=404, detail="Student not found")
    if result == "EMAIL_ALREADY_EXISTS":
        raise HTTPException(
            status_code=409,
            detail="Email already registered for another student"
        )
    return result


@router.get("/{student_id}/eligible-schemes", response_model=list[EligibilityCheckResponse])
def get_student_eligible_schemes_api(
    student_id: str,
    db: Session = Depends(get_db)
):
    result = evaluate_student_for_all_schemes(db, student_id)
    if result == "STUDENT_NOT_FOUND":
        raise HTTPException(status_code=404, detail="Student not found")
    return result


@router.post("/{student_id}/documents/upload", response_model=DocumentResponse)
async def upload_student_document_api(
    student_id: str,
    file: UploadFile = File(...),
    document_type: str = Form(...),
    db: Session = Depends(get_db),
):
    # 1. Validate document_type
    if document_type not in ALLOWED_DOCUMENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid document_type '{document_type}'. Allowed types: {', '.join(sorted(ALLOWED_DOCUMENT_TYPES))}",
        )

    # 2. Validate PDF format
    if not (file.filename and file.filename.lower().endswith(".pdf")):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed",
        )

    # 3. Read content and validate max 5 MB size
    content = await file.read()
    if len(content) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=400,
            detail="File size exceeds maximum limit of 5 MB",
        )

    # 4. Check student existence
    student = get_student(db, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # 5. Store file under backend/uploads
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    safe_name = f"{student_id}_{uuid.uuid4().hex[:8]}_{Path(file.filename).name}"
    target_path = UPLOAD_DIR / safe_name
    with open(target_path, "wb") as f:
        f.write(content)

    # 6. Save document record
    doc = upload_student_document(
        db=db,
        student_id=student_id,
        document_type=document_type,
        filename=file.filename,
        file_path=str(target_path),
    )

    return doc