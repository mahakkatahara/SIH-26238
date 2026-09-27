from app.seed import DEMO_STUDENT_ID, DEMO_SCHOLARSHIPS


def test_eligibility_check_student_not_found(client, seeded_db):
    response = client.post(
        "/api/v1/eligibility/check",
        json={
            "student_id": "non-existent-student",
            "scholarship_id": DEMO_SCHOLARSHIPS[0]["id"],
        },
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Student not found"


def test_eligibility_check_scholarship_not_found(client, seeded_db):
    response = client.post(
        "/api/v1/eligibility/check",
        json={
            "student_id": DEMO_STUDENT_ID,
            "scholarship_id": "non-existent-scholarship",
        },
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Scholarship not found"


def test_eligibility_check_success_mock_contract(client, seeded_db):
    response = client.post(
        "/api/v1/eligibility/check",
        json={
            "student_id": DEMO_STUDENT_ID,
            "scholarship_id": DEMO_SCHOLARSHIPS[0]["id"],
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["student_id"] == DEMO_STUDENT_ID
    assert data["scholarship_id"] == DEMO_SCHOLARSHIPS[0]["id"]
    assert data["eligible"] is True
    assert isinstance(data["reasons"], list)
    # Limitation disclosure verification
    assert data["evaluation_mode"] == "MOCK"
