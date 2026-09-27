from app.seed import DEMO_STUDENT_ID


def test_list_mock_digilocker_documents(client, seeded_db):
    response = client.get(f"/api/v1/students/{DEMO_STUDENT_ID}/digilocker/documents")
    assert response.status_code == 200
    docs = response.json()
    assert len(docs) == 4
    types = [d["document_type"] for d in docs]
    assert "MOCK_ST_CERTIFICATE" in types
    assert "MOCK_INCOME_CERTIFICATE" in types


def test_import_mock_digilocker_document(client, seeded_db):
    # Import MOCK_CLASS_12_MARKSHEET (not yet in seeded documents for this student)
    response = client.post(
        f"/api/v1/students/{DEMO_STUDENT_ID}/digilocker/documents/import",
        json={"document_type": "MOCK_CLASS_12_MARKSHEET"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["student_id"] == DEMO_STUDENT_ID
    assert data["document_type"] == "MOCK_CLASS_12_MARKSHEET"
    assert data["status"] == "PENDING"

    # Attempting to re-import should fail with 409
    dup_res = client.post(
        f"/api/v1/students/{DEMO_STUDENT_ID}/digilocker/documents/import",
        json={"document_type": "MOCK_CLASS_12_MARKSHEET"},
    )
    assert dup_res.status_code == 409
    assert dup_res.json()["detail"] == "Mock DigiLocker document already imported"
