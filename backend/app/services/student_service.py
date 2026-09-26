from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.student import Student
from app.schemas.student import StudentCreate


def create_student(db: Session, student: StudentCreate):
    new_student = Student(
        name=student.name,
        email=student.email
    )

    db.add(new_student)

    try:
        db.commit()
        db.refresh(new_student)
    except IntegrityError:
        db.rollback()
        return None

    return new_student


def get_students(db: Session):
    return db.query(Student).all()