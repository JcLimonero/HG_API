import configparser
import math
import pyodbc

_config = configparser.ConfigParser()
_config.read("config.ini")

BASE_QUERY = """
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
"""

COUNT_QUERY = f"SELECT COUNT(*) FROM ({BASE_QUERY}) AS _count"

PAGINATED_QUERY = (
    BASE_QUERY.rstrip()
    + "\nORDER BY (SELECT NULL)\nOFFSET {offset} ROWS FETCH NEXT {page_size} ROWS ONLY"
)


def get_ordenes(page: int, page_size: int) -> dict:
    dsn = _config.get("database", "dsn")
    conn = pyodbc.connect(f"DSN={dsn}")
    cursor = None
    try:
        cursor = conn.cursor()

        cursor.execute(COUNT_QUERY)
        total = cursor.fetchone()[0]

        offset = (page - 1) * page_size
        sql = PAGINATED_QUERY.format(offset=offset, page_size=page_size)
        cursor.execute(sql)
        columns = [col[0] for col in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
    finally:
        if cursor:
            cursor.close()
        conn.close()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": math.ceil(total / page_size) if page_size else 0,
        "data": rows,
    }
