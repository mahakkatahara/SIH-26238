from pydantic import BaseModel


class ApplicationDocumentCreate(BaseModel):
    document_id: str


class ApplicationDocumentResponse(BaseModel):
    application_id: str
    document_id: str

    class Config:
        from_attributes = True
