# Sistema Web de Consulta y Análisis de Datos Abiertos de Colombia

**Asignatura:** Desarrollo de Aplicaciones con Acceso a Datos
**Integrantes:**
- Santiago Alvear – API y datos: _nombre_
- Kener Quezada – SQL Server y Modelo: _nombre_
- Diego Rodriguez – Controlador y Vista: _nombre_

## Objetivo
Aplicación web en Flask que consulta una API de datos.gov.co, guarda los registros recibidos en SQL Server y permite consultarlos desde el navegador con un filtro de búsqueda y un resumen numérico, aplicando el patrón MVC. No implementa CRUD: solo sincroniza, guarda y consulta.

## Dataset elegido
- **Nombre:** Casos positivos de COVID-19 en Colombia
- **Entidad:** Instituto Nacional de Salud (INS), publicado en datos.gov.co
- **Propósito:** consolidado nacional de casos positivos de COVID-19; permite analizar la distribución por territorio, edad, sexo y estado del paciente.
- **Ficha:** https://www.datos.gov.co/Salud-y-Protecci-n-Social/Casos-positivos-de-COVID-19-en-Colombia/gt2j-8ykr
- **ID del recurso:** `gt2j-8ykr`
- **Endpoint (SODA):** `https://www.datos.gov.co/resource/gt2j-8ykr.json?$limit=100&$order=id_de_caso`
- **Identificador estable:** `id_de_caso`, guardado en `id_api` (columna UNIQUE para evitar duplicados).

## Campos usados
| Campo API | Columna SQL | Descripción |
|---|---|---|
| id_de_caso | id_api | Identificador único del caso |
| departamento_nom | departamento | Departamento de residencia |
| ciudad_municipio_nom | municipio | Municipio de residencia |
| edad | edad | Edad del paciente |
| unidad_medida | unidad_medida | Unidad de la edad: 1 = años, 2 = meses, 3 = días |
| sexo | sexo | F / M |
| estado | estado | Leve, Moderado, Grave, Fallecido |
| fecha_diagnostico | fecha_diagnostico | Fecha de diagnóstico (AAAA-MM-DD) |

El JSON completo de cada registro se conserva en `json_original`.

**Notas:**
- El resumen calcula la edad promedio solo con casos medidos en años, porque la API mezcla años, meses y días.
- La API se consulta con `$order=id_de_caso` y `$limit=100`, por lo que siempre trae los mismos 100 primeros casos. Una segunda sincronización inserta 0 registros nuevos (comprueba que no se duplica).

## Requisitos
Python 3.10+, SQL Server + SSMS, Microsoft ODBC Driver 18 for SQL Server, navegador web.

## Instalación
1. Crear y activar el entorno virtual:
   `python -m venv venv` y `.\venv\Scripts\Activate.ps1` (PowerShell).
2. `pip install -r requirements.txt`
3. Ejecutar `sql/crear_base_datos.sql` en SSMS (crea la BD `DatosAbiertosDB` y la tabla `RegistrosAPI`; se puede ejecutar más de una vez).
4. Copiar `.env.example` como `.env` y ajustar:
   - `DB_SERVER` (`localhost`, o `localhost\SQLEXPRESS` si usan SQL Server Express).
   - `DB_TRUSTED=yes` para autenticación de Windows, o `no` con `DB_USER` y `DB_PASSWORD`.
   - `SECRET_KEY` con una clave propia.

   El archivo `.env` no se sube al repositorio.

## Ejecución
```
python app.py
```
Abrir http://127.0.0.1:5000, pulsar **Consultar API y guardar datos** y usar el buscador (municipio, departamento o estado).

## Estructura MVC
```
proyecto_datos_abiertos/
├── app.py                  # Controlador (rutas / y /sincronizar)
├── api/api_client.py       # Servicio: consumo de la API externa
├── models/datos_model.py   # Modelo: conexión, INSERT, SELECT y resumen en SQL Server
├── templates/index.html    # Vista (Jinja2)
├── static/estilos.css      # Estilos de la vista
├── sql/crear_base_datos.sql
├── .env.example
├── requirements.txt
└── README.md
```
- **Modelo:** único archivo que habla con SQL Server (consultas parametrizadas).
- **Vista:** solo presenta datos; no contiene SQL.
- **Controlador:** recibe las solicitudes, llama al servicio de API o al modelo y elige la plantilla.

## Flujo
Navegador → Controlador (`app.py`) → API Client / Modelo (SQL Server) → Controlador → Vista (HTML) → Navegador.

## Seguridad básica
Sin credenciales en el código, `.env` fuera del repositorio, consultas parametrizadas, `debug=True` solo en desarrollo local.

## Evidencias
Se entregan aparte: respuesta JSON de la API, registros en SQL Server y capturas de la aplicación.
