def test_user_registration_and_login(client, db_session):
    # Register user
    reg_res = client.post(
        "/api/v1/users",
        json={
            "name": "Test Applicant",
            "email": "applicant.test@example.com",
            "password": "SecretPassword123!",
        },
    )
    assert reg_res.status_code == 200
    user_data = reg_res.json()
    assert "id" in user_data
    assert user_data["email"] == "applicant.test@example.com"

    # Duplicate registration
    dup_res = client.post(
        "/api/v1/users",
        json={
            "name": "Test Applicant",
            "email": "applicant.test@example.com",
            "password": "AnotherPassword123!",
        },
    )
    assert dup_res.status_code == 409

    # Valid Login
    login_res = client.post(
        "/api/v1/users/login",
        json={
            "email": "applicant.test@example.com",
            "password": "SecretPassword123!",
        },
    )
    assert login_res.status_code == 200
    assert login_res.json()["email"] == "applicant.test@example.com"

    # Invalid Login
    bad_login = client.post(
        "/api/v1/users/login",
        json={
            "email": "applicant.test@example.com",
            "password": "WrongPassword!",
        },
    )
    assert bad_login.status_code == 401


def test_student_creation_and_listing(client, db_session):
    # Create user first
    user_res = client.post(
        "/api/v1/users",
        json={
            "name": "Student User",
            "email": "student.profile@example.com",
            "password": "Password123!",
        },
    )
    assert user_res.status_code == 200
    user_id = user_res.json()["id"]

    # Create student profile
    student_res = client.post(
        "/api/v1/students",
        json={
            "user_id": user_id,
            "name": "Student Profile",
            "email": "student.profile@example.com",
        },
    )
    assert student_res.status_code == 200
    student_data = student_res.json()
    assert student_data["user_id"] == user_id

    # List students
    list_res = client.get("/api/v1/students")
    assert list_res.status_code == 200
    assert len(list_res.json()) >= 1
