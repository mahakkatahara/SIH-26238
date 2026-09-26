from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate
from app.repositories.user_repository import (
    create_user,
    get_user_by_email
)


def register_user(db: Session, user: UserCreate):
    existing_user = get_user_by_email(db, user.email)

    if existing_user:
        return None

    new_user = User(
        name=user.name,
        email=user.email,
        password=user.password
    )

    return create_user(db, new_user)