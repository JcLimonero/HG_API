import math
from unittest.mock import MagicMock, patch, call
import pytest


def _make_row(values: dict):
    """Build a mock pyodbc row with dict-like column access via cursor.description."""
    return list(values.values())


def _mock_connection(count: int, rows: list):
    """
    Return a mock pyodbc connection whose cursor executes two queries:
    1. COUNT query  → returns [(count,)]
    2. Data query   → returns list of rows (each row is a list of values)
    The cursor.description matches the 12 expected columns.
    """
    columns = [
        "Orden de Reparacion", "Numero de Chasis", "Modelo", "Version",
        "Kilometraje", "Fecha Ultima Visita", "ND", "Nombre del Cliente",
        "Telefono", "Correo Flujo Informacion", "Dt Venda", "Operacion",
    ]
    description = [(col, None, None, None, None, None, None) for col in columns]

    cursor = MagicMock()
    cursor.description = description
    # fetchone returns count, fetchall returns data rows
    cursor.fetchone.return_value = (count,)
    cursor.fetchall.return_value = [list(r.values()) for r in rows]

    conn = MagicMock()
    conn.cursor.return_value = cursor
    return conn, cursor


def test_get_ordenes_returns_correct_structure():
    sample_row = {
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
    conn, cursor = _mock_connection(count=1, rows=[sample_row])

    with patch("database.pyodbc.connect", return_value=conn):
        import database
        result = database.get_ordenes(page=1, page_size=50)

    assert result["total"] == 1
    assert result["page"] == 1
    assert result["page_size"] == 50
    assert result["pages"] == 1
    assert len(result["data"]) == 1
    assert result["data"][0]["Orden de Reparacion"] == "OS-001"
    assert result["data"][0]["Nombre del Cliente"] == "Juan Perez"


def test_get_ordenes_calculates_pages_correctly():
    conn, _ = _mock_connection(count=101, rows=[])
    with patch("database.pyodbc.connect", return_value=conn):
        import database
        result = database.get_ordenes(page=1, page_size=50)
    assert result["pages"] == 3  # ceil(101/50)


def test_get_ordenes_closes_connection_on_success():
    conn, _ = _mock_connection(count=0, rows=[])
    with patch("database.pyodbc.connect", return_value=conn):
        import database
        database.get_ordenes(page=1, page_size=50)
    conn.close.assert_called_once()


def test_get_ordenes_closes_connection_on_error():
    conn = MagicMock()
    conn.cursor.side_effect = Exception("cursor error")
    with patch("database.pyodbc.connect", return_value=conn):
        import database
        with pytest.raises(Exception, match="cursor error"):
            database.get_ordenes(page=1, page_size=50)
    conn.close.assert_called_once()


def test_get_ordenes_passes_correct_offset_to_query():
    conn, cursor = _mock_connection(count=200, rows=[])
    with patch("database.pyodbc.connect", return_value=conn):
        import database
        database.get_ordenes(page=3, page_size=50)
    # Second execute call is the paginated query; check OFFSET value
    paginated_call_args = cursor.execute.call_args_list[1]
    sql = paginated_call_args[0][0]
    assert "OFFSET 100 ROWS" in sql
    assert "FETCH NEXT 50 ROWS ONLY" in sql
