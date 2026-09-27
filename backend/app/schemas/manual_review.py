from pydantic import BaseModel


class ManualReviewResponse(BaseModel):
    id: str
    application_id: str
    verification_id: str
    status: str

    class Config:
        from_attributes = True
