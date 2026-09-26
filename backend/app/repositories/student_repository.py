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