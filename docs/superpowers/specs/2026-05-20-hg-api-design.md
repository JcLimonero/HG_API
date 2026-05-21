# HG API — Design Spec
Date: 2026-05-20

## Overview

A single-endpoint REST API built with FastAPI (Python 3.11) that exposes repair orders from a database accessible via ODBC DSN. The API is protected by an API key and supports pagination.

---

## Architecture

### File Structure

```
HG_API/
├── main.py          # FastAPI app, router, auth dependency
├── database.py      # pyodbc connection, query execution, SQL pagination
├── config.ini       # Configuration (not versioned)
├── requirements.txt # Python dependencies
└── .gitignore       # Excludes config.ini, __pycache__, .env
```

No subdirectories — single endpoint does not justify further structure.

### Components

**`config.ini`**
Holds the API key and database DSN. Not committed to version control.

```ini
[api]
api_key = mi-clave-secreta

[database]
dsn = JUAREZ
```

**`main.py`**
- Instantiates the FastAPI app
- Reads `config.ini` at startup via `configparser`
- Defines a `verify_api_key` dependency that reads the `X-API-Key` header and returns HTTP 401 if it does not match the configured key
- Defines `GET /ordenes-reparacion` with query params `page: int = 1` and `page_size: int = 50`
- Calls `database.get_ordenes(page, page_size)` and returns the result
- Returns HTTP 500 with `{"detail": "<message>"}` on database errors

**`database.py`**
- Reads DSN from `config.ini` via `configparser`
- `get_ordenes(page, page_size)` function:
  1. Opens a pyodbc connection using the DSN
  2. Executes a `COUNT(*)` wrapper around the base query to get `total`
  3. Executes the base query with `OFFSET` / `FETCH NEXT` for the requested page
  4. Closes the connection in a `finally` block (no connection pooling)
  5. Returns `{"total": int, "page": int, "page_size": int, "pages": int, "data": list[dict]}`
- Raises exceptions on connection or query errors (caught and surfaced as HTTP 500 in `main.py`)

---

## Endpoint

### `GET /ordenes-reparacion`

**Security:** Requires header `X-API-Key: <configured_key>`. Returns `401 Unauthorized` if missing or incorrect.

**Query parameters:**

| Parameter   | Type | Default | Description              |
|-------------|------|---------|--------------------------|
| `page`      | int  | 1       | Page number (1-indexed)  |
| `page_size` | int  | 50      | Records per page         |

**Base query (executed as-is):**

```sql
select
  o."Nr OS" as 'Orden de Reparacion',
  a."Chassi" as 'Numero de Chasis',
  v."Nm Modelo" as 'Modelo',
  v."Versao" as 'Version',
  a."Quilometragem" as 'Kilometraje',
  o."Dt Fechamento" as 'Fecha Ultima Visita',
  a."Cliente Veiculo" as 'ND',
  e."Razao Social" as 'Nombre del Cliente',
  LTRIM(CONCAT(e."Nr DD1",e."Tel1")) as 'Telefono',
  e."email" as 'Correo Flujo Informacion',
  v."Dt Venda",
  ap."Comentario" as 'Operacion'
From "OS" as o
inner join "Atendimento" as a on o."Nr Atendimento"=a."Nr Atendimento"
inner join "Veiculos" as v on 'Numero de Chasis'=v."Chassi"
inner join "Entidades" as e on a."Cliente Veiculo"=e."Cod Entidade"
left join "Atendimento Pacotes" as ap on o."Nr Atendimento"=ap."Nr Atendimento"
Where o.Situacao ='R'
```

Pagination is applied by wrapping this query with `OFFSET (page-1)*page_size ROWS FETCH NEXT page_size ROWS ONLY`.

**Success response (HTTP 200):**

```json
{
  "total": 320,
  "page": 1,
  "page_size": 50,
  "pages": 7,
  "data": [
    {
      "Orden de Reparacion": "...",
      "Numero de Chasis": "...",
      "Modelo": "...",
      "Version": "...",
      "Kilometraje": "...",
      "Fecha Ultima Visita": "...",
      "ND": "...",
      "Nombre del Cliente": "...",
      "Telefono": "...",
      "Correo Flujo Informacion": "...",
      "Dt Venda": "...",
      "Operacion": "..."
    }
  ]
}
```

JSON keys match exactly the SQL column aliases.

**Error responses:**

| Status | Condition                        |
|--------|----------------------------------|
| 401    | Missing or invalid `X-API-Key`   |
| 500    | Database connection or query error |

---

## Dependencies (`requirements.txt`)

```
fastapi
uvicorn[standard]
pyodbc
```

Python version: 3.11

---

## `.gitignore`

Excludes: `config.ini`, `__pycache__/`, `*.pyc`, `.env`, `.venv/`

---

## Data Flow

```
Client
  │  GET /ordenes-reparacion?page=1&page_size=50
  │  Header: X-API-Key: <key>
  ▼
main.py
  ├─ verify_api_key() → 401 if key mismatch
  └─ get_ordenes(page=1, page_size=50)
       ├─ pyodbc.connect(DSN)
       ├─ COUNT(*) query → total
       ├─ paginated query → rows
       ├─ connection.close() [finally]
       └─ return {total, page, page_size, pages, data}
  └─ HTTP 200 JSON  /  HTTP 500 on exception
```
