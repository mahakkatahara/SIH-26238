import uuid
import pytest
from fastapi.testclient import TestClient

from app.core.database import SessionLocal
from app.main import app
from app.models.scholarship import Scholarship
from app.models.student import Student
from app.models.user import User
from app.services.eligibility_service import (
    evaluate_student_rules,
    format_inr,
)

client = TestClient(app)


@pytest.fixture(scope="module")
def db_session():
    db = SessionLocal()
    yield db
    db.close()


@pytest.fixture(scope="module")
def test_user(db_session):
    unique_email = f"user_{uuid.uuid4().hex[:8]}@example.com"
    user = User(
        name="Test User",
        email=unique_email,
        password="hashed_pw",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(scope="module")
def schemes(db_session):
    all_schemes = db_session.query(Scholarship).all()
    scheme_map = {s.code: s for s in all_schemes}
    return scheme_map


# -------------------------------------------------------------
# 1. PRE_MATRIC_ST TESTS
# -------------------------------------------------------------

def test_pre_matric_eligible(schemes):
    scheme = schemes["PRE_MATRIC_ST"]
    student = Student(
        id=str(uuid.uuid4()),
        name="Pre Matric Student",
        email="pre@example.com",
        tribe_status="ST",
        annual_family_income=200000,
        education_level="CLASS_9",
    )
    result = evaluate_student_rules(student, scheme)
    assert result["eligible"] is True
    assert result["evaluation_mode"] == "RULES_V1"
    assert "Student meets all eligibility criteria" in result["reasons"][0]


def test_pre_matric_over_income(schemes):
    scheme = schemes["PRE_MATRIC_ST"]
    student = Student(
        id=str(uuid.uuid4()),
        name="Pre Matric Student",
        email="pre_over@example.com",
        tribe_status="ST",
        annual_family_income=310000,
        education_level="CLASS_9",
    )
    result = evaluate_student_rules(student, scheme)
    assert result["eligible"] is False
    assert result["evaluation_mode"] == "RULES_V1"
    assert any("Family income Rs 3,10,000 exceeds limit of Rs 2,50,000" in r for r in result["reasons"])


def test_pre_matric_wrong_level(schemes):
    scheme = schemes["PRE_MATRIC_ST"]
    student = Student(
        id=str(uuid.uuid4()),
        name="Pre Matric Student",
        email="pre_level@example.com",
        tribe_status="ST",
        annual_family_income=200000,
        education_level="CLASS_11",
    )
    result = evaluate_student_rules(student, scheme)
    assert result["eligible"] is False
    assert any("Education level CLASS_11 is not eligible for PRE_MATRIC_ST" in r for r in result["reasons"])


def test_pre_matric_missing_data(schemes):
    scheme = schemes["PRE_MATRIC_ST"]
    student = Student(
        id=str(uuid.uuid4()),
        name="Pre Matric Student",
        email="pre_miss@example.com",
        tribe_status="ST",
        annual_family_income=None,  # Missing income
        education_level="CLASS_9",
    )
    result = evaluate_student_rules(student, scheme)
    assert result["eligible"] is False
    assert "Missing: annual_family_income" in result["reasons"]


# -------------------------------------------------------------
# 2. POST_MATRIC_ST TESTS
# -------------------------------------------------------------

def test_post_matric_eligible(schemes):
    scheme = schemes["POST_MATRIC_ST"]
    student = Student(
        id=str(uuid.uuid4()),
        name="Post Matric Student",
        email="post@example.com",
        tribe_status="PVTG",
        annual_family_income=240000,
        education_level="UG",
    )
    result = evaluate_student_rules(student, scheme)
    assert result["eligible"] is True
    assert result["evaluation_mode"] == "RULES_V1"


def test_post_matric_over_income(schemes):
    scheme = schemes["POST_MATRIC_ST"]
    student = Student(
        id=str(uuid.uuid4()),
        name="Post Matric Student",
        email="post_over@example.com",
        tribe_status="ST",
        annual_family_income=310000,
        education_level="UG",
    )
    result = evaluate_student_rules(student, scheme)
    assert result["eligible"] is False
    assert any("Family income Rs 3,10,000 exceeds limit of Rs 2,50,000" in r for r in result["reasons"])


def test_post_matric_wrong_level(schemes):
    scheme = schemes["POST_MATRIC_ST"]
    student = Student(
        id=str(uuid.uuid4()),
        name="Post Matric Student",
        email="post_wrong@example.com",
        tribe_status="ST",
        annual_family_income=200000,
        education_level="CLASS_9",
    )
    result = evaluate_student_rules(student, scheme)
    assert result["eligible"] is False
    assert any("Education level CLASS_9 is not eligible for POST_MATRIC_ST" in r for r in result["reasons"])


def test_post_matric_missing_data(schemes):
    scheme = schemes["POST_MATRIC_ST"]
    student = Student(
        id=str(uuid.uuid4()),
        name="Post Matric Student",
        email="post_miss@example.com",
        tribe_status="ST",
        annual_family_income=200000,
        education_level=None,  # Missing education level
    )
    result = evaluate_student_rules(student, scheme)
    assert result["eligible"] is False
    assert "Missing: education_level" in result["reasons"]


# -------------------------------------------------------------
# 3. TOP_CLASS_ST TESTS
# -------------------------------------------------------------

def test_top_class_eligible(schemes):
    scheme = schemes["TOP_CLASS_ST"]
    student = Student(
        id=str(uuid.uuid4()),
        name="Top Class Student",
        email="top@example.com",
        tribe_status="ST",
        annual_family_income=500000,
        education_level="UG",
        institution_name="indian institute of technology bombay",  # From top_class_institutes.json, lowercase
    )
    result = evaluate_student_rules(student, scheme)
    assert result["eligible"] is True
    assert result["evaluation_mode"] == "RULES_V1"


def test_top_class_over_income(schemes):
    scheme = schemes["TOP_CLASS_ST"]
    student = Student(
        id=str(uuid.uuid4()),
        name="Top Class Student",
        email="top_over@example.com",
        tribe_status="ST",
        annual_family_income=700000,
        education_level="UG",
        institution_name="IIT Bombay",
    )
    result = evaluate_student_rules(student, scheme)
    assert result["eligible"] is False
    assert any("Family income Rs 7,00,000 exceeds limit of Rs 6,00,000" in r for r in result["reasons"])


def test_top_class_non_premier_institute(schemes):
    scheme = schemes["TOP_CLASS_ST"]
    student = Student(
        id=str(uuid.uuid4()),
        name="Top Class Student",
        email="top_nonprem@example.com",
        tribe_status="ST",
        annual_family_income=500000,
        education_level="UG",
        institution_name="Random Unaffiliated College",
    )
    result = evaluate_student_rules(student, scheme)
    assert result["eligible"] is False
    assert any("is not in the notified premier institutes list" in r for r in result["reasons"])


def test_top_class_missing_data(schemes):
    scheme = schemes["TOP_CLASS_ST"]
    student = Student(
        id=str(uuid.uuid4()),
        name="Top Class Student",
        email="top_miss@example.com",
        tribe_status="ST",
        annual_family_income=500000,
        education_level="UG",
        institution_name=None,  # Missing institution name
    )
    result = evaluate_student_rules(student, scheme)
    assert result["eligible"] is False
    assert "Missing: institution_name" in result["reasons"]


# -------------------------------------------------------------
# 4. NATIONAL_FELLOWSHIP_ST TESTS
# -------------------------------------------------------------

def test_national_fellowship_eligible(schemes):
    scheme = schemes["NATIONAL_FELLOWSHIP_ST"]
    student = Student(
        id=str(uuid.uuid4()),
        name="Fellowship Student",
        email="fellow@example.com",
        tribe_status="ST",
        annual_family_income=1200000,  # No income ceiling applies
        education_level="PHD",
    )
    result = evaluate_student_rules(student, scheme)
    assert result["eligible"] is True


def test_national_fellowship_wrong_level(schemes):
    scheme = schemes["NATIONAL_FELLOWSHIP_ST"]
    student = Student(
        id=str(uuid.uuid4()),
        name="Fellowship Student",
        email="fellow_wrong@example.com",
        tribe_status="ST",
        annual_family_income=300000,
        education_level="UG",
    )
    result = evaluate_student_rules(student, scheme)
    assert result["eligible"] is False
    assert any("Education level UG is not eligible for NATIONAL_FELLOWSHIP_ST" in r for r in result["reasons"])


def test_national_fellowship_missing_data(schemes):
    scheme = schemes["NATIONAL_FELLOWSHIP_ST"]
    student = Student(
        id=str(uuid.uuid4()),
        name="Fellowship Student",
        email="fellow_miss@example.com",
        tribe_status="ST",
        annual_family_income=300000,
        education_level=None,  # Missing education level
    )
    result = evaluate_student_rules(student, scheme)
    assert result["eligible"] is False
    assert "Missing: education_level" in result["reasons"]


# -------------------------------------------------------------
# 5. NATIONAL_OVERSEAS_ST TESTS
# -------------------------------------------------------------

def test_national_overseas_eligible(schemes):
    scheme = schemes["NATIONAL_OVERSEAS_ST"]
    student = Student(
        id=str(uuid.uuid4()),
        name="Overseas Student",
        email="overseas@example.com",
        tribe_status="ST",
        annual_family_income=550000,
        education_level="PG",
        study_country="United Kingdom",
    )
    result = evaluate_student_rules(student, scheme)
    assert result["eligible"] is True


def test_national_overseas_over_income(schemes):
    scheme = schemes["NATIONAL_OVERSEAS_ST"]
    student = Student(
        id=str(uuid.uuid4()),
        name="Overseas Student",
        email="overseas_over@example.com",
        tribe_status="ST",
        annual_family_income=650000,
        education_level="PG",
        study_country="USA",
    )
    result = evaluate_student_rules(student, scheme)
    assert result["eligible"] is False
    assert any("Family income Rs 6,50,000 exceeds limit of Rs 6,00,000" in r for r in result["reasons"])


def test_national_overseas_wrong_level(schemes):
    scheme = schemes["NATIONAL_OVERSEAS_ST"]
    student = Student(
        id=str(uuid.uuid4()),
        name="Overseas Student",
        email="overseas_wrong@example.com",
        tribe_status="ST",
        annual_family_income=500000,
        education_level="CLASS_12",
        study_country="Germany",
    )
    result = evaluate_student_rules(student, scheme)
    assert result["eligible"] is False
    assert any("Education level CLASS_12 is not eligible for NATIONAL_OVERSEAS_ST" in r for r in result["reasons"])


def test_national_overseas_missing_study_country(schemes):
    scheme = schemes["NATIONAL_OVERSEAS_ST"]
    student = Student(
        id=str(uuid.uuid4()),
        name="Overseas Student",
        email="overseas_miss_country@example.com",
        tribe_status="ST",
        annual_family_income=500000,
        education_level="PG",
        study_country=None,  # Missing study_country
    )
    result = evaluate_student_rules(student, scheme)
    assert result["eligible"] is False
    assert "Missing: study_country" in result["reasons"]


def test_national_overseas_study_in_india_ineligible(schemes):
    scheme = schemes["NATIONAL_OVERSEAS_ST"]
    student = Student(
        id=str(uuid.uuid4()),
        name="Overseas Student",
        email="overseas_india@example.com",
        tribe_status="ST",
        annual_family_income=500000,
        education_level="PG",
        study_country="India",  # Study in India is not eligible
    )
    result = evaluate_student_rules(student, scheme)
    assert result["eligible"] is False
    assert "National Overseas Scholarship is only for study abroad" in result["reasons"]


def test_national_overseas_missing_data(schemes):
    scheme = schemes["NATIONAL_OVERSEAS_ST"]
    student = Student(
        id=str(uuid.uuid4()),
        name="Overseas Student",
        email="overseas_miss@example.com",
        tribe_status=None,  # Missing tribe status
        annual_family_income=500000,
        education_level="PG",
        study_country="Canada",
    )
    result = evaluate_student_rules(student, scheme)
    assert result["eligible"] is False
    assert "Missing: tribe_status" in result["reasons"]


# -------------------------------------------------------------
# 6. API ENDPOINTS INTEGRATION TESTS
# -------------------------------------------------------------

def test_api_student_profile_update_and_eligible_schemes(db_session, test_user):
    # 1. Create a student via POST /api/v1/students
    unique_email = f"student_{uuid.uuid4().hex[:8]}@example.com"
    create_res = client.post(
        "/api/v1/students",
        json={
            "user_id": test_user.id,
            "name": "Integration Student",
            "email": unique_email,
        }
    )
    assert create_res.status_code == 200
    student_data = create_res.json()
    student_id = student_data["id"]

    # Initially missing profile data
    check_all_res = client.get(f"/api/v1/students/{student_id}/eligible-schemes")
    assert check_all_res.status_code == 200
    evaluations = check_all_res.json()
    assert len(evaluations) == 5
    for ev in evaluations:
        assert ev["eligible"] is False
        assert any(r.startswith("Missing:") for r in ev["reasons"])

    # 2. Update profile via PATCH /api/v1/students/{id}
    update_res = client.patch(
        f"/api/v1/students/{student_id}",
        json={
            "tribe_status": "ST",
            "state": "Odisha",
            "annual_family_income": 200000,
            "education_level": "CLASS_9",
            "institution_name": "Government High School",
            "is_hosteller": False,
        }
    )
    assert update_res.status_code == 200
    updated_profile = update_res.json()
    assert updated_profile["tribe_status"] == "ST"
    assert updated_profile["annual_family_income"] == 200000
    assert updated_profile["education_level"] == "CLASS_9"

    # 3. Check eligible schemes again
    check_after_res = client.get(f"/api/v1/students/{student_id}/eligible-schemes")
    assert check_after_res.status_code == 200
    evaluations_after = check_after_res.json()
    eval_by_code = {e["scholarship_code"]: e for e in evaluations_after}

    # PRE_MATRIC_ST should now be eligible!
    assert eval_by_code["PRE_MATRIC_ST"]["eligible"] is True
    assert eval_by_code["PRE_MATRIC_ST"]["evaluation_mode"] == "RULES_V1"

    # POST_MATRIC_ST should be ineligible (wrong education level CLASS_9)
    assert eval_by_code["POST_MATRIC_ST"]["eligible"] is False
    assert any("CLASS_9 is not eligible" in r for r in eval_by_code["POST_MATRIC_ST"]["reasons"])

    # 4. Check single eligibility check endpoint POST /api/v1/eligibility/check
    pm_id = eval_by_code["PRE_MATRIC_ST"]["scholarship_id"]
    single_check_res = client.post(
        "/api/v1/eligibility/check",
        json={"student_id": student_id, "scholarship_id": pm_id}
    )
    assert single_check_res.status_code == 200
    single_data = single_check_res.json()
    assert single_data["eligible"] is True
    assert single_data["evaluation_mode"] == "RULES_V1"
