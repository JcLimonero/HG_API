import configparser
from unittest.mock import patch
from fastapi.testclient import TestClient

API_KEY = "test-key"


def _make_client():
    cfg = configparser.ConfigParser()
    cfg["api"] = {"api_key": API_KEY}
    cfg["database"] = {"dsn": "FAKE"}
    import importlib
    import sys
    # Remove main from cache to force fresh import
    if "main" in sys.modules:
        del sys.modules["main"]
    # Patch at the point where config.read is called
    with patch("main.configparser.ConfigParser.read"):
        import main
        # Replace the config object with our test config
        main.config = cfg
        return TestClient(main.app)


SAMPLE_RESULT = {
    "total": 2,
    "page": 1,
    "page_size": 50,
    "pages": 1,
    "data": [
        {
            "Orden de Reparacion": "OS-001",
            "Numero de Chasis": "CH123",
            "Modelo": "Gol",
            "Version": "1.0",
            "Kilometraje": 50000,
            "Fecha Ultima Visita": "2024-01-01",
            "ND": "C001",
            "Nombre del Cliente": "Juan Perez",
            "Telefono": "555-1234",
            "Correo Flujo Informacion": "juan@example.com",
            "Dt Venda": "2020-06-15",
            "Operacion": "Cambio de aceite",
        }
    ],
}


def test_endpoint_returns_200_with_valid_key():
    client = _make_client()
    with patch("database.get_ordenes", return_value=SAMPLE_RESULT):
        response = client.get(
            "/ordenes-reparacion", headers={"X-API-Key": API_KEY}
        )
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 2
    assert body["page"] == 1
    assert body["pages"] == 1
    assert isinstance(body["data"], list)


def test_endpoint_passes_pagination_params():
    client = _make_client()
    with patch("database.get_ordenes", return_value={**SAMPLE_RESULT, "page": 2, "page_size": 10}) as mock_db:
        response = client.get(
            "/ordenes-reparacion?page=2&page_size=10",
            headers={"X-API-Key": API_KEY},
        )
    mock_db.assert_called_once_with(2, 10)
    assert response.status_code == 200


def test_endpoint_returns_500_on_db_error():
    client = _make_client()
    with patch("database.get_ordenes", side_effect=Exception("connection refused")):
        response = client.get(
            "/ordenes-reparacion", headers={"X-API-Key": API_KEY}
        )
    assert response.status_code == 500
    assert "connection refused" in response.json()["detail"]


def test_endpoint_default_pagination():
    client = _make_client()
    with patch("database.get_ordenes", return_value=SAMPLE_RESULT) as mock_db:
        client.get("/ordenes-reparacion", headers={"X-API-Key": API_KEY})
    mock_db.assert_called_once_with(1, 50)
