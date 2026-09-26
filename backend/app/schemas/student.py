from pydantic import BaseModel, EmailStr


class StudentCreate(BaseModel):
    name: str
    email: EmailStr


class StudentResponse(BaseModel):
    id: str
    name: str
    email: str

    class Config:
        from_attributes = True