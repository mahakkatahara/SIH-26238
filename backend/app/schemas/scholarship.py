from pydantic import BaseModel


class ScholarshipResponse(BaseModel):
    id: str
    code: str
    name: str

    class Config:
        from_attributes = True
