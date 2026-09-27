from pydantic import BaseModel


class DocumentCreate(BaseModel):
    student_id: str
    document_type: str
    document_name: str


class DocumentResponse(BaseModel):
    id: str
    student_id: str
    document_type: str
    document_name: str
    status: str

    class Config:
        from_attributes = True
