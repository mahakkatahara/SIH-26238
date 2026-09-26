from sqlalchemy.orm import Session

from app.models.student import Student
from app.schemas.student import StudentCreate
from app.repositories.student_repository import (
    create_student,
    get_students,
    get_student_by_email,
    get_student_by_user_id
)
from app.repositories.user_repository import get_user_by_id


def add_student(db: Session, student: StudentCreate):
    user = get_user_by_id(db, student.user_id)
    if not user:
        return "USER_NOT_FOUND"

    existing_student_for_user = get_student_by_user_id(db, student.user_id)
    if existing_student_for_user:
        return "STUDENT_ALREADY_EXISTS"

    existing_student_email = get_student_by_email(db, student.email)
    if existing_student_email:
        return "EMAIL_ALREADY_EXISTS"

    new_student = Student(
        user_id=student.user_id,
        name=student.name,
        email=student.email
    )

    return create_student(db, new_student)


def list_students(db: Session):
    return get_students(db)