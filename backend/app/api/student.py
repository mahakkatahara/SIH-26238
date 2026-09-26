from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.schemas.student import StudentCreate, StudentResponse
from app.services.student_service import create_student, get_students

router = APIRouter(prefix="/students", tags=["Students"])


@router.post("/", response_model=StudentResponse)
def add_student(student: StudentCreate, db: Session = Depends(get_db)):
    result = create_student(db, student)

    if result is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=409, detail="Email already exists")

    return result


@router.get("/", response_model=list[StudentResponse])
def list_students(db: Session = Depends(get_db)):
    return get_students(db)