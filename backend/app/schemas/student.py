from pydantic import BaseModel, EmailStr


class StudentCreate(BaseModel):
    user_id: str
    name: str
    email: EmailStr


class StudentResponse(BaseModel):
    id: str
    user_id: str | None = None
    name: str
    email: str

    class Config:
        from_attributes = True