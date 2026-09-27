from app.seed import DEMO_STUDENT_ID


def test_list_documents(client, seeded_db):
    response = client.get("/api/v1/documents")
    assert response.status_code == 200
    docs = response.json()
    assert len(docs) >= 1
    doc = docs[0]
    assert "id" in doc
    assert "student_id" in doc
    assert "document_type" in doc
    assert "document_name" in doc
    assert doc["status"] in ["PENDING", "VERIFIED", "EXPIRED", "REJECTED"]


def test_create_document_success(client, seeded_db):
    response = client.post(
        "/api/v1/documents",
        json={
            "student_id": DEMO_STUDENT_ID,
            "document_type": "MOCK_INCOME_CERTIFICATE",
            "document_name": "Annual Income Certificate",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["student_id"] == DEMO_STUDENT_ID
    assert data["document_type"] == "MOCK_INCOME_CERTIFICATE"
    assert data["status"] == "PENDING"


def test_create_document_student_not_found(client, seeded_db):
    response = client.post(
        "/api/v1/documents",
        json={
            "student_id": "non-existent-student",
            "document_type": "MOCK_INCOME_CERTIFICATE",
            "document_name": "Annual Income Certificate",
        },
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Student not found"
