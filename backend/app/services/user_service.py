from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate, UserLogin
from app.repositories.user_repository import (
    create_user,
    get_user_by_email
)
from app.core.security import hash_password, verify_password


def register_user(db: Session, user: UserCreate):
    existing_user = get_user_by_email(db, user.email)

    if existing_user:
        return None

    hashed_password = hash_password(user.password)

    new_user = User(
        name=user.name,
        email=user.email,
        password=hashed_password
    )

    return create_user(db, new_user)


def login_user(db: Session, user: UserLogin):
    existing_user = get_user_by_email(db, user.email)

    if existing_user is None:
        return None

    if not verify_password(user.password, existing_user.password):
        return None

    return existing_user