from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.schemas.user import UserCreate, UserLogin, UserResponse
from app.services.user_service import register_user, login_user

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("", response_model=UserResponse)
@router.post("/", response_model=UserResponse, include_in_schema=False)
def register_user_api(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    result = register_user(db, user)

    if result is None:
        raise HTTPException(
            status_code=409,
            detail="Email already exists"
        )

    return result


@router.post("/login", response_model=UserResponse)
@router.post("/login/", response_model=UserResponse, include_in_schema=False)
def login_user_api(
    user: UserLogin,
    db: Session = Depends(get_db)
):
    result = login_user(db, user)

    if result is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    return result