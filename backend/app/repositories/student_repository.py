from sqlalchemy.orm import Session
from app.models.student import Student


def create_student(db: Session, student: Student):
    db.add(student)
    db.commit()
    db.refresh(student)
    return student


def get_students(db: Session):
    return db.query(Student).all()


def get_student_by_email(db: Session, email: str):
    return db.query(Student).filter(Student.email == email).first()


def get_student_by_user_id(db: Session, user_id: str):
    return db.query(Student).filter(Student.user_id == user_id).first()


def get_student_by_id(db: Session, student_id: str):
    return db.query(Student).filter(Student.id == student_id).first()


def update_student(db: Session, student: Student, update_data: dict) -> Student:
    for field, value in update_data.items():
        if hasattr(student, field):
            setattr(student, field, value)
    db.commit()
    db.refresh(student)
    return student