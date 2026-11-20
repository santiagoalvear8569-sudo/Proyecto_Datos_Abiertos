import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash
from api.api_client import APIClient
from models.datos_model import (
    guardar_registros, consultar_registros, obtener_resumen
)

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "cambiar-por-una-clave-local")


@app.route("/", methods=["GET"])
def inicio():
    filtro = request.args.get("q", "").strip()
    try:
        registros = consultar_registros(filtro)
        resumen = obtener_resumen()
    except Exception:
        app.logger.exception("Error al consultar la base de datos")
        flash("No fue posible consultar la base de datos. Revise la conexión y el .env.", "error")
        registros = []
        resumen = {"total": 0, "edad_promedio": None, "por_estado": []}
    return render_template(
        "index.html", registros=registros, filtro=filtro, resumen=resumen
    )


@app.route("/sincronizar", methods=["POST"])
def sincronizar():
    try:
        cliente = APIClient()
        datos = cliente.obtener_registros(100)
        cantidad = guardar_registros(datos)
        flash(f"Consulta terminada. Nuevos registros guardados: {cantidad}", "success")
    except Exception:
        app.logger.exception("Error al sincronizar")
        flash("No fue posible consultar la API o guardar los datos. Revise la consola.", "error")
    return redirect(url_for("inicio"))


if __name__ == "__main__":
    app.run(debug=True)
