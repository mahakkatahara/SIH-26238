from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.schemas.eligibility import EligibilityCheckResponse
from app.schemas.student import StudentCreate, StudentResponse, StudentUpdate
from app.services.eligibility_service import evaluate_student_for_all_schemes
from app.services.student_service import (
    add_student,
    get_student,
    list_students,
    update_student_profile,
)

router = APIRouter(prefix="/students", tags=["Students"])


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