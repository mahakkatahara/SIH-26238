from app.seed import DEMO_STUDENT_ID, DEMO_SCHOLARSHIPS, DEMO_DOCUMENTS


def test_list_applications_seeded(client, seeded_db):
    response = client.get("/api/v1/applications")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["status"] in ["DRAFT", "SUBMITTED", "IN_VERIFICATION"]


def test_create_application_success(client, seeded_db):
    response = client.post(
        "/api/v1/applications",
        json={
            "student_id": DEMO_STUDENT_ID,
            "scholarship_id": DEMO_SCHOLARSHIPS[1]["id"],
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["student_id"] == DEMO_STUDENT_ID
    assert data["scholarship_id"] == DEMO_SCHOLARSHIPS[1]["id"]
    assert data["status"] == "DRAFT"


def test_create_application_student_not_found(client, seeded_db):
    response = client.post(
        "/api/v1/applications",
        json={
            "student_id": "non-existent-student",
            "scholarship_id": DEMO_SCHOLARSHIPS[0]["id"],
        },
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Student not found"


def test_create_application_scholarship_not_found(client, seeded_db):
    response = client.post(
        "/api/v1/applications",
        json={
            "student_id": DEMO_STUDENT_ID,
            "scholarship_id": "non-existent-scholarship",
        },
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Scholarship not found"


def test_link_document_to_application_and_list(client, seeded_db):
    # Create fresh application
    app_res = client.post(
        "/api/v1/applications",
        json={
            "student_id": DEMO_STUDENT_ID,
            "scholarship_id": DEMO_SCHOLARSHIPS[0]["id"],
        },
    )
    app_id = app_res.json()["id"]

    # Link existing document
    doc_id = DEMO_DOCUMENTS[0]["id"]
    link_res = client.post(
        f"/api/v1/applications/{app_id}/documents",
        json={"document_id": doc_id},
    )
    assert link_res.status_code == 200
    assert link_res.json() == {"application_id": app_id, "document_id": doc_id}

    # Attempt duplicate link
    dup_res = client.post(
        f"/api/v1/applications/{app_id}/documents",
        json={"document_id": doc_id},
    )
    assert dup_res.status_code == 409
    assert dup_res.json()["detail"] == "Document already linked to application"

    # List linked documents
    list_res = client.get(f"/api/v1/applications/{app_id}/documents")
    assert list_res.status_code == 200
    docs = list_res.json()
    assert len(docs) == 1
    assert docs[0]["id"] == doc_id
