from sqlalchemy.orm import Session

from app.models.student import Student
from app.schemas.student import StudentCreate
from app.repositories.student_repository import (
    create_student,
    get_students,
    get_student_by_email
)


def add_student(db: Session, student: StudentCreate):
    existing_student = get_student_by_email(db, student.email)

    if existing_student:
        return None

    new_student = Student(
        name=student.name,
        email=student.email
    )

    return create_student(db, new_student)


def list_students(db: Session):
    return get_students(db)