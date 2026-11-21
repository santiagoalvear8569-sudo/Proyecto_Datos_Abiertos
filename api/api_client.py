import os
import requests
from dotenv import load_dotenv

load_dotenv()


class APIClient:
    def __init__(self):
        recurso = os.getenv("API_RESOURCE_ID")
        self.url = f"https://www.datos.gov.co/resource/{recurso}.json"

    def obtener_registros(self, limite=100):
        parametros = {"$limit": limite, "$order": "id_de_caso"}
        respuesta = requests.get(self.url, params=parametros, timeout=20)
        respuesta.raise_for_status()
        return respuesta.json()
