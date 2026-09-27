from sqlalchemy.orm import Session

from app.models.student import Student
from app.schemas.student import StudentCreate, StudentUpdate
from app.repositories.student_repository import (
    create_student,
    get_students,
    get_student_by_email,
    get_student_by_user_id,
    get_student_by_id,
    update_student,
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
        email=student.email,
        tribe_status=student.tribe_status,
        state=student.state,
        annual_family_income=student.annual_family_income,
        education_level=student.education_level,
        institution_name=student.institution_name,
        is_hosteller=student.is_hosteller,
        date_of_birth=student.date_of_birth,
        study_country=student.study_country,
    )

    return create_student(db, new_student)


def list_students(db: Session):
    return get_students(db)


def get_student(db: Session, student_id: str):
    return get_student_by_id(db, student_id)


def update_student_profile(db: Session, student_id: str, payload: StudentUpdate):
    student = get_student_by_id(db, student_id)
    if not student:
        return None

    update_data = payload.model_dump(exclude_unset=True)
    if not update_data:
        return student

    # If email is being updated, check if it's already used by another student
    if "email" in update_data and update_data["email"] != student.email:
        existing_email = get_student_by_email(db, update_data["email"])
        if existing_email and existing_email.id != student_id:
            return "EMAIL_ALREADY_EXISTS"

    return update_student(db, student, update_data)