from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.schemas.student import StudentCreate, StudentResponse
from app.services.student_service import add_student, list_students

router = APIRouter(prefix="/students", tags=["Students"])


@router.post("/", response_model=StudentResponse)
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


@router.get("/", response_model=list[StudentResponse])
def list_students_api(db: Session = Depends(get_db)):
    return list_students(db)