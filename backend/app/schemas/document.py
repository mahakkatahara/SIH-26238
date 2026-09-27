from pydantic import BaseModel


class DocumentCreate(BaseModel):
    student_id: str
    document_type: str
    document_name: str
    file_path: str | None = None
    source: str | None = None


class DocumentResponse(BaseModel):
    id: str
    student_id: str
    document_type: str
    document_name: str
    file_path: str | None = None
    source: str | None = None
    status: str

    class Config:
        from_attributes = True
