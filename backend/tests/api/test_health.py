from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import get_db


def test_health_check_success(client: TestClient):
    """Test health check endpoint returns 200 OK and connected status when DB is healthy."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data == {"status": "ok", "db": "connected"}


def test_health_check_db_failure():
    """Test health check endpoint returns 503 Service Unavailable when DB connection fails."""
    mock_db = MagicMock()
    mock_db.execute.side_effect = Exception("DB Connection Refused")

    def override_get_db_failure():
        yield mock_db

    app.dependency_overrides[get_db] = override_get_db_failure
    try:
        with TestClient(app) as test_client:
            response = test_client.get("/api/health")
            assert response.status_code == 503
            data = response.json()
            assert data["detail"]["status"] == "error"
            assert data["detail"]["db"] == "disconnected"
            assert "DB Connection Refused" in data["detail"]["error"]
    finally:
        app.dependency_overrides.clear()
