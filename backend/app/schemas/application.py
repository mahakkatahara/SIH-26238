from pydantic import BaseModel


class ApplicationCreate(BaseModel):
    student_id: str
    scholarship_id: str


class ApplicationResponse(BaseModel):
    id: str
    student_id: str
    scholarship_id: str
    status: str

    class Config:
        from_attributes = True


class ApplicationStatusTransitionRequest(BaseModel):
    status: str


class ApplicationStatusHistoryResponse(BaseModel):
    id: str
    application_id: str
    from_status: str
    to_status: str

    class Config:
        from_attributes = True
