from pydantic import BaseModel


class EligibilityCheckRequest(BaseModel):
    student_id: str
    scholarship_id: str


class EligibilityCheckResponse(BaseModel):
    student_id: str
    scholarship_id: str
    scholarship_code: str | None = None
    scholarship_name: str | None = None
    eligible: bool
    reasons: list[str]
    evaluation_mode: str
