import os
import json
import pyodbc
from dotenv import load_dotenv

load_dotenv()


def obtener_conexion():
    servidor = os.getenv("DB_SERVER")
    base_datos = os.getenv("DB_NAME")
    driver = os.getenv("DB_DRIVER", "ODBC Driver 18 for SQL Server")
    trusted = os.getenv("DB_TRUSTED", "yes").lower() == "yes"

    if trusted:
        cadena = (
            f"DRIVER={{{driver}}};"
            f"SERVER={servidor};"
            f"DATABASE={base_datos};"
            "Trusted_Connection=yes;"
            "TrustServerCertificate=yes;"
        )
    else:
        usuario = os.getenv("DB_USER")
        clave = os.getenv("DB_PASSWORD")
        cadena = (
            f"DRIVER={{{driver}}};"
            f"SERVER={servidor};"
            f"DATABASE={base_datos};"
            f"UID={usuario};PWD={clave};"
            "TrustServerCertificate=yes;"
        )
    return pyodbc.connect(cadena)


def _a_entero(valor):
    try:
        return int(valor)
    except (TypeError, ValueError):
        return None


def guardar_registros(registros):
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    insertados = 0

    try:
        for registro in registros:
            identificador = str(registro.get("id_de_caso") or "")
            if not identificador:
                continue

            # AAAA-MM-DD; si no viene fecha se guarda NULL
            fecha = (registro.get("fecha_diagnostico") or "")[:10] or None

            cursor.execute(
                """
                IF NOT EXISTS (
                    SELECT 1 FROM RegistrosAPI WHERE id_api = ?
                )
                INSERT INTO RegistrosAPI
                (id_api, departamento, municipio, edad, unidad_medida,
                 sexo, estado, fecha_diagnostico, json_original)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                identificador,
                identificador,
                registro.get("departamento_nom"),
                registro.get("ciudad_municipio_nom"),
                _a_entero(registro.get("edad")),
                str(registro.get("unidad_medida") or "") or None,
                registro.get("sexo"),
                registro.get("estado"),
                fecha,
                json.dumps(registro, ensure_ascii=False)
            )
            if cursor.rowcount > 0:
                insertados += 1

        conexion.commit()
        return insertados
    except Exception:
        conexion.rollback()
        raise
    finally:
        cursor.close()
        conexion.close()


def consultar_registros(filtro=""):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        if filtro:
            cursor.execute(
                """
                SELECT TOP 100 id_api, departamento, municipio, edad,
                       unidad_medida, sexo, estado, fecha_diagnostico
                FROM RegistrosAPI
                WHERE municipio LIKE ?
                   OR departamento LIKE ?
                   OR estado LIKE ?
                ORDER BY id DESC
                """,
                f"%{filtro}%", f"%{filtro}%", f"%{filtro}%"
            )
        else:
            cursor.execute(
                """
                SELECT TOP 100 id_api, departamento, municipio, edad,
                       unidad_medida, sexo, estado, fecha_diagnostico
                FROM RegistrosAPI
                ORDER BY id DESC
                """
            )

        columnas = [c[0] for c in cursor.description]
        return [dict(zip(columnas, fila)) for fila in cursor.fetchall()]
    finally:
        cursor.close()
        conexion.close()


def obtener_resumen():
    """Resumen numérico: total, edad promedio (solo casos medidos en años)
    y conteo por estado."""
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        cursor.execute("SELECT COUNT(*) FROM RegistrosAPI")
        total = cursor.fetchone()[0]

        # La edad viene con unidad (1=años, 2=meses, 3=días): se promedian solo años.
        cursor.execute(
            "SELECT AVG(CAST(edad AS FLOAT)) FROM RegistrosAPI "
            "WHERE unidad_medida = '1' AND edad IS NOT NULL"
        )
        promedio = cursor.fetchone()[0]

        cursor.execute(
            """
            SELECT ISNULL(estado, 'Sin dato') AS estado, COUNT(*) AS cantidad
            FROM RegistrosAPI
            GROUP BY estado
            ORDER BY cantidad DESC
            """
        )
        por_estado = [{"estado": f[0], "cantidad": f[1]} for f in cursor.fetchall()]

        return {
            "total": total,
            "edad_promedio": round(promedio, 1) if promedio is not None else None,
            "por_estado": por_estado,
        }
    finally:
        cursor.close()
        conexion.close()
