# HG API — Referencia de API

**Versión:** 1.0  
**Base URL:** `http://<servidor>:8084`

---

## Autenticación

Todos los endpoints requieren el header `X-API-Key` con la clave configurada en el servidor.

```
X-API-Key: <clave>
```

Si el header está ausente o la clave es incorrecta, el servidor retorna `401 Unauthorized`.

---

## Endpoints

### GET /ordenes-reparacion

Retorna las órdenes de reparación con estado `R` (Reparadas), con soporte de paginación y filtros por fecha.

#### Parámetros de consulta

| Parámetro      | Tipo   | Requerido | Default | Descripción                                      |
|----------------|--------|-----------|---------|--------------------------------------------------|
| `page`         | int    | No        | `1`     | Número de página (empieza en 1)                  |
| `page_size`    | int    | No        | `50`    | Cantidad de registros por página                 |
| `fecha_desde`  | string | No        | —       | Fecha de inicio en formato `YYYYMMDD`            |
| `fecha_hasta`  | string | No        | —       | Fecha de fin en formato `YYYYMMDD`               |

#### Ejemplos de request

**Todos los registros (primera página):**
```
GET /ordenes-reparacion
X-API-Key: <clave>
```

**Con paginación:**
```
GET /ordenes-reparacion?page=2&page_size=100
X-API-Key: <clave>
```

**Filtrar desde una fecha:**
```
GET /ordenes-reparacion?fecha_desde=20260101
X-API-Key: <clave>
```

**Filtrar por rango de fechas:**
```
GET /ordenes-reparacion?fecha_desde=20260101&fecha_hasta=20260531
X-API-Key: <clave>
```

**Rango de fechas con paginación:**
```
GET /ordenes-reparacion?fecha_desde=20260101&fecha_hasta=20260531&page=2&page_size=50
X-API-Key: <clave>
```

---

#### Respuesta exitosa — `200 OK`

```json
{
  "total": 320,
  "page": 1,
  "page_size": 50,
  "pages": 7,
  "data": [
    {
      "Orden de Reparacion": "OS-00123",
      "Numero de Chasis": "9BWZZZ377VT004251",
      "Modelo": "Gol",
      "Version": "1.0",
      "Kilometraje": 85000,
      "Fecha Ultima Visita": "20260515",
      "ND": "C00456",
      "Nombre del Cliente": "Juan Perez",
      "Telefono": "5551234567",
      "Correo Flujo Informacion": "juan.perez@email.com",
      "Dt Venda": "20210310",
      "Operacion": "Cambio de aceite y filtros"
    }
  ]
}
```

#### Campos de la respuesta

**Envelope de paginación:**

| Campo       | Tipo | Descripción                              |
|-------------|------|------------------------------------------|
| `total`     | int  | Total de registros que coinciden         |
| `page`      | int  | Página actual                            |
| `page_size` | int  | Registros por página solicitados         |
| `pages`     | int  | Total de páginas disponibles             |
| `data`      | list | Lista de órdenes de reparación           |

**Campos de cada orden (`data[]`):**

| Campo                    | Tipo   | Descripción                                     |
|--------------------------|--------|-------------------------------------------------|
| `Orden de Reparacion`    | string | Número de orden de servicio                     |
| `Numero de Chasis`       | string | Número de chasis del vehículo                   |
| `Modelo`                 | string | Modelo del vehículo                             |
| `Version`                | string | Versión del modelo                              |
| `Kilometraje`            | int    | Kilometraje registrado en la visita             |
| `Fecha Ultima Visita`    | string | Fecha de cierre de la OS en formato `YYYYMMDD`  |
| `ND`                     | string | Código interno del cliente                      |
| `Nombre del Cliente`     | string | Razón social del cliente                        |
| `Telefono`               | string | Teléfono concatenado (código de área + número)  |
| `Correo Flujo Informacion` | string | Correo electrónico del cliente               |
| `Dt Venda`               | string | Fecha de venta del vehículo en formato `YYYYMMDD` |
| `Operacion`              | string | Descripción de la operación realizada           |

---

#### Respuestas de error

**`401 Unauthorized` — API key ausente o incorrecta:**
```json
{
  "detail": "Unauthorized"
}
```

**`500 Internal Server Error` — Error de base de datos:**
```json
{
  "detail": "Descripción del error"
}
```

---

## Notas de implementación

- El campo `Fecha Ultima Visita` usa formato `YYYYMMDD` — los filtros `fecha_desde` y `fecha_hasta` deben usar el mismo formato.
- Los filtros de fecha son inclusivos en ambos extremos.
- Si no se especifican fechas, retorna todos los registros con `Situacao = 'R'`.
- Los campos `Telefono` y `Correo Flujo Informacion` pueden estar vacíos si no están registrados.
- El campo `Operacion` puede ser `null` si la orden no tiene paquetes asociados.
