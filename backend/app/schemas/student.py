from datetime import date
from pydantic import BaseModel, EmailStr


class StudentCreate(BaseModel):
    user_id: str
    name: str
    email: EmailStr
    tribe_status: str | None = None
    state: str | None = None
    annual_family_income: int | None = None
    education_level: str | None = None
    institution_name: str | None = None
    is_hosteller: bool | None = None
    date_of_birth: date | None = None
    study_country: str | None = None


class StudentUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    tribe_status: str | None = None
    state: str | None = None
    annual_family_income: int | None = None
    education_level: str | None = None
    institution_name: str | None = None
    is_hosteller: bool | None = None
    date_of_birth: date | None = None
    study_country: str | None = None


class StudentResponse(BaseModel):
    id: str
    user_id: str | None = None
    name: str
    email: str
    tribe_status: str | None = None
    state: str | None = None
    annual_family_income: int | None = None
    education_level: str | None = None
    institution_name: str | None = None
    is_hosteller: bool | None = None
    date_of_birth: date | None = None
    study_country: str | None = None

    class Config:
        from_attributes = True