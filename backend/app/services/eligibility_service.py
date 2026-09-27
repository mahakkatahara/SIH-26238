from sqlalchemy.orm import Session
from app.repositories.student_repository import get_student_by_id
from app.repositories.scholarship_repository import get_scholarship_by_id
from app.schemas.eligibility import EligibilityCheckRequest, EligibilityCheckResponse


def evaluate_mock_eligibility(student, scholarship) -> dict:
    """Isolated mock eligibility evaluator for Phase 1.
    
    This is NOT an official government or MoTA rules engine.
    Official criteria (income, category, marks, age, etc.) are not configured.
    """
    return {
        "eligible": True,
        "reasons": [
            "Mock eligibility evaluation only; official scheme rules are not configured"
        ],
        "evaluation_mode": "MOCK",
    }


def check_eligibility(db: Session, request: EligibilityCheckRequest):
    student = get_student_by_id(db, request.student_id)
    if not student:
        return "STUDENT_NOT_FOUND"

    scholarship = get_scholarship_by_id(db, request.scholarship_id)
    if not scholarship:
        return "SCHOLARSHIP_NOT_FOUND"

    eval_result = evaluate_mock_eligibility(student, scholarship)

    return EligibilityCheckResponse(
        student_id=request.student_id,
        scholarship_id=request.scholarship_id,
        eligible=eval_result["eligible"],
        reasons=eval_result["reasons"],
        evaluation_mode=eval_result["evaluation_mode"],
    )
