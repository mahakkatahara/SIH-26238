from pydantic import BaseModel


class PaymentResponse(BaseModel):
    id: str
    application_id: str
    status: str

    class Config:
        from_attributes = True


class PaymentStatusTransitionRequest(BaseModel):
    status: str
