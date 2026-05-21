import configparser
from unittest.mock import patch
from fastapi.testclient import TestClient


def make_client(api_key: str = "test-key"):
    """Patch config so tests don't need a real config.ini."""
    cfg = configparser.ConfigParser()
    cfg["api"] = {"api_key": api_key}
    cfg["database"] = {"dsn": "FAKE_DSN"}
    with patch("main.config", cfg):
        from main import app
        return TestClient(app)


def test_missing_api_key_returns_401():
    client = make_client()
    response = client.get("/ordenes-reparacion")
    assert response.status_code == 401


def test_wrong_api_key_returns_401():
    client = make_client()
    response = client.get("/ordenes-reparacion", headers={"X-API-Key": "wrong"})
    assert response.status_code == 401


def test_correct_api_key_does_not_return_401():
    client = make_client(api_key="test-key")
    # Will hit the DB layer and fail with 500, but NOT 401
    with patch("database.get_ordenes", side_effect=Exception("db error")):
        response = client.get(
            "/ordenes-reparacion", headers={"X-API-Key": "test-key"}
        )
    assert response.status_code != 401
