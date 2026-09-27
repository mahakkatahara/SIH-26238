from app.seed import DEMO_APPLICATION_ID, DEMO_DOCUMENTS


def test_list_application_verifications(client, seeded_db):
    response = client.get(f"/api/v1/applications/{DEMO_APPLICATION_ID}/verifications")
    assert response.status_code == 200
    records = response.json()
    assert len(records) >= 1
    rec = records[0]
    assert rec["application_id"] == DEMO_APPLICATION_ID
    assert rec["status"] in ["PENDING", "VERIFIED", "MISMATCH", "MANUAL_REVIEW", "FAILED"]


def test_create_verification_record_duplicate(client, seeded_db):
    # The seeded database already has a verification record for DEMO_DOCUMENTS[0]
    response = client.post(
        f"/api/v1/applications/{DEMO_APPLICATION_ID}/verifications",
        json={"document_id": DEMO_DOCUMENTS[0]["id"]},
    )
    assert response.status_code == 409
    assert response.json()["detail"] == "Verification record already exists"


def test_execute_verification_success(client, seeded_db):
    # DEMO_DOCUMENTS[1] is TEST_VERIFIED and linked to DEMO_APPLICATION_ID
    create_res = client.post(
        f"/api/v1/applications/{DEMO_APPLICATION_ID}/verifications",
        json={"document_id": DEMO_DOCUMENTS[1]["id"]},
    )
    assert create_res.status_code == 200
    verif_id = create_res.json()["id"]

    # Execute verification
    exec_res = client.post(f"/api/v1/verifications/{verif_id}/execute")
    assert exec_res.status_code == 200
    data = exec_res.json()
    assert data["id"] == verif_id
    assert data["status"] == "VERIFIED"
    assert data["evaluation_mode"] == "MOCK"

    # Re-executing non-pending record should return 409
    reexec_res = client.post(f"/api/v1/verifications/{verif_id}/execute")
    assert reexec_res.status_code == 409
    assert reexec_res.json()["detail"] == "Verification record is not pending"
