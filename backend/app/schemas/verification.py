from pydantic import BaseModel


class VerificationCreate(BaseModel):
    document_id: str


class VerificationRecordResponse(BaseModel):
    id: str
    application_id: str
    document_id: str
    status: str

    class Config:
        from_attributes = True
