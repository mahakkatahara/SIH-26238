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


class VerificationExecutionResponse(BaseModel):
    id: str
    application_id: str
    document_id: str
    status: str
    message: str
    evaluation_mode: str

