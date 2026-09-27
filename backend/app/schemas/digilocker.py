from pydantic import BaseModel


class MockDigiLockerDocument(BaseModel):
    document_type: str
    document_name: str


class MockDigiLockerImportRequest(BaseModel):
    document_type: str
