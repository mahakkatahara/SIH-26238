import json
from pathlib import Path
from typing import Any
from sqlalchemy.orm import Session

from app.models.scholarship import Scholarship
from app.models.student import Student
from app.repositories.scholarship_repository import get_scholarship_by_id, get_scholarships
from app.repositories.student_repository import get_student_by_id
from app.schemas.eligibility import EligibilityCheckRequest, EligibilityCheckResponse

EVALUATION_MODE = "RULES_V1"

DATA_FILE_PATH = Path(__file__).resolve().parent.parent / "data" / "top_class_institutes.json"


def load_top_class_institutes() -> tuple[set[str], list[str]]:
    """Loads premier institutes and keywords from backend/app/data/top_class_institutes.json."""
    if not DATA_FILE_PATH.exists():
        return set(), []
    try:
        with open(DATA_FILE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            institutes = {inst.lower().strip() for inst in data.get("institutes", [])}
            keywords = [kw.lower().strip() for kw in data.get("keywords", [])]
            return institutes, keywords
    except Exception:
        return set(), []


TOP_CLASS_INSTITUTES, TOP_CLASS_KEYWORDS = load_top_class_institutes()


def format_inr(number: int) -> str:
    """Format an integer in the Indian numbering format (e.g. 2,50,000)."""
    s = str(abs(number))
    if len(s) <= 3:
        formatted = s
    else:
        last_three = s[-3:]
        remaining = s[:-3]
        parts = []
        while len(remaining) > 2:
            parts.append(remaining[-2:])
            remaining = remaining[:-2]
        if remaining:
            parts.append(remaining)
        parts.reverse()
        formatted = ",".join(parts) + "," + last_three
    return f"-{formatted}" if number < 0 else formatted


def is_premier_institute(institution_name: str | None) -> bool:
    if not institution_name:
        return False
    name_clean = institution_name.lower().strip()
    # Match exact institute name or contains in listed institutes case-insensitively
    if name_clean in TOP_CLASS_INSTITUTES or any(name_clean == inst or inst in name_clean for inst in TOP_CLASS_INSTITUTES):
        return True
    # Match recognized premier keywords case-insensitively
    return any(keyword in name_clean for keyword in TOP_CLASS_KEYWORDS)


def evaluate_student_rules(student: Student, scholarship: Scholarship) -> dict[str, Any]:
    """Deterministic, explainable rules engine for MoTA ST scholarship schemes."""
    reasons: list[str] = []
    missing_fields: list[str] = []

    # 1. Missing Data Checks
    if not student.tribe_status:
        missing_fields.append("Missing: tribe_status")

    if not student.education_level:
        missing_fields.append("Missing: education_level")

    if scholarship.income_ceiling is not None and student.annual_family_income is None:
        missing_fields.append("Missing: annual_family_income")

    if scholarship.code == "TOP_CLASS_ST" and not student.institution_name:
        missing_fields.append("Missing: institution_name")

    if scholarship.code == "NATIONAL_OVERSEAS_ST" and not student.study_country:
        missing_fields.append("Missing: study_country")

    if missing_fields:
        return {
            "eligible": False,
            "reasons": missing_fields,
            "evaluation_mode": EVALUATION_MODE,
        }

    # 2. Tribe Status Validation (must be ST or PVTG)
    valid_tribe_statuses = {"ST", "PVTG"}
    normalized_tribe = student.tribe_status.upper().strip() if student.tribe_status else ""
    if normalized_tribe not in valid_tribe_statuses:
        reasons.append(f"Tribe status must be ST or PVTG (found: {student.tribe_status})")

    # 3. Income Ceiling Check
    if scholarship.income_ceiling is not None and student.annual_family_income is not None:
        if student.annual_family_income > scholarship.income_ceiling:
            reasons.append(
                f"Family income Rs {format_inr(student.annual_family_income)} "
                f"exceeds limit of Rs {format_inr(scholarship.income_ceiling)}"
            )

    # 4. Education Level Check
    if scholarship.eligible_levels:
        student_level = student.education_level.upper().strip() if student.education_level else ""
        eligible_levels_upper = [lvl.upper().strip() for lvl in scholarship.eligible_levels]
        if student_level not in eligible_levels_upper:
            reasons.append(
                f"Education level {student.education_level} is not eligible for "
                f"{scholarship.code} (eligible: {', '.join(scholarship.eligible_levels)})"
            )

    # 5. Scheme-Specific Checks
    if scholarship.code == "TOP_CLASS_ST":
        if not is_premier_institute(student.institution_name):
            reasons.append(
                f"Institution '{student.institution_name}' is not in the notified premier institutes list"
            )

    if scholarship.code == "NATIONAL_OVERSEAS_ST":
        if student.study_country and student.study_country.strip().lower() == "india":
            reasons.append("National Overseas Scholarship is only for study abroad")

    # Final Outcome Determination
    if not reasons:
        return {
            "eligible": True,
            "reasons": [f"Student meets all eligibility criteria for {scholarship.name}"],
            "evaluation_mode": EVALUATION_MODE,
        }

    return {
        "eligible": False,
        "reasons": reasons,
        "evaluation_mode": EVALUATION_MODE,
    }


def check_eligibility(db: Session, request: EligibilityCheckRequest):
    student = get_student_by_id(db, request.student_id)
    if not student:
        return "STUDENT_NOT_FOUND"

    scholarship = get_scholarship_by_id(db, request.scholarship_id)
    if not scholarship:
        return "SCHOLARSHIP_NOT_FOUND"

    eval_result = evaluate_student_rules(student, scholarship)

    return EligibilityCheckResponse(
        student_id=request.student_id,
        scholarship_id=request.scholarship_id,
        scholarship_code=scholarship.code,
        scholarship_name=scholarship.name,
        eligible=eval_result["eligible"],
        reasons=eval_result["reasons"],
        evaluation_mode=eval_result["evaluation_mode"],
    )


def evaluate_student_for_all_schemes(db: Session, student_id: str):
    student = get_student_by_id(db, student_id)
    if not student:
        return "STUDENT_NOT_FOUND"

    scholarships = get_scholarships(db)
    results: list[EligibilityCheckResponse] = []

    for scholarship in scholarships:
        if not scholarship.is_active:
            continue
        eval_result = evaluate_student_rules(student, scholarship)
        results.append(
            EligibilityCheckResponse(
                student_id=student.id,
                scholarship_id=scholarship.id,
                scholarship_code=scholarship.code,
                scholarship_name=scholarship.name,
                eligible=eval_result["eligible"],
                reasons=eval_result["reasons"],
                evaluation_mode=eval_result["evaluation_mode"],
            )
        )

    return results
