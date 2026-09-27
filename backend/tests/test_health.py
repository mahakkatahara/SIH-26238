from unittest.mock import patch


def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "message" in data


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_db_connected(client):
    # Mocking engine.connect to verify connected response contract
    class MockConnection:
        def __enter__(self):
            return self
        def __exit__(self, exc_type, exc_val, exc_tb):
            pass
        def execute(self, statement):
            return True

    with patch("app.main.engine.connect", return_value=MockConnection()):
        response = client.get("/health/db")
        assert response.status_code == 200
        assert response.json() == {"status": "ok", "database": "connected"}


def test_health_db_disconnected(client):
    with patch("app.main.engine.connect", side_effect=Exception("Database connection timeout")):
        response = client.get("/health/db")
        assert response.status_code == 503
        data = response.json()
        assert data["status"] == "error"
        assert data["database"] == "disconnected"
        # Secrets/passwords must never leak
        assert "password" not in str(data).lower()
        assert "timeout" not in str(data).lower()


def test_db_test_endpoint_backward_compatibility(client):
    class MockConnection:
        def __enter__(self):
            return self
        def __exit__(self, exc_type, exc_val, exc_tb):
            pass
        def execute(self, statement):
            return True

    with patch("app.main.engine.connect", return_value=MockConnection()):
        response = client.get("/db-test")
        assert response.status_code == 200
        assert response.json() == {"status": "ok", "database": "connected"}
