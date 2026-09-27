from pydantic import BaseModel


class EligibilityCheckRequest(BaseModel):
    student_id: str
    scholarship_id: str


class EligibilityCheckResponse(BaseModel):
    student_id: str
    scholarship_id: str
    eligible: bool
    reasons: list[str]
    evaluation_mode: str
