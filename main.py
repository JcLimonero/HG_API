import configparser
import math
from pathlib import Path
from fastapi import FastAPI, Header, HTTPException, Depends, Query

config = configparser.ConfigParser()
config.read(Path(__file__).parent / "config.ini")

app = FastAPI()


def verify_api_key(x_api_key: str = Header(default=None)):
    expected = config.get("api", "api_key")
    if x_api_key != expected:
        raise HTTPException(status_code=401, detail="Unauthorized")


@app.get("/ordenes-reparacion")
def get_ordenes_reparacion(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1),
    fecha_desde: str = Query(default=None, description="Fecha inicio en formato YYYYMMDD"),
    fecha_hasta: str = Query(default=None, description="Fecha fin en formato YYYYMMDD"),
    _: None = Depends(verify_api_key),
):
    import database
    try:
        result = database.get_ordenes(page, page_size, fecha_desde, fecha_hasta)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return result
