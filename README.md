# Actividades Costeras – Reto Grafana HACKUDC 2026

Proyecto de solución al reto de Grafana: **recomendación para actividades costeras en A Coruña** con una puntuación del **1 al 10** (condiciones en la costa), apoyado en **sistemas de alerta** y **Grafana** para visualización. **Ubicación fija: A Coruña** (no se pueden consultar otras localidades).

## Qué incluye

- **Docker Compose** para levantar de forma reproducible:
  - **PostgreSQL**: base de datos donde se guardan datos meteorológicos y recomendaciones.
  - **Grafana**: dashboards y alertas sobre esos datos.
  - **Backend** (FastAPI): obtiene datos, calcula el score 1-10 y expone la API.

- **Motor de datos: Open-Meteo** (sin API key):
  - **Weather API**: viento (km/h) y precipitación.
  - **Marine API**: oleaje (altura de ola, periodo).

- **Sistema de recomendación 1-10**: el backend combina viento, oleaje y precipitación y devuelve:
  - **Score** de 1 (muy desaconsejado) a 10 (excelente).
  - **Explicación** en texto (por qué ese score).
  - **Mensaje** resumido (ej. "Buenas condiciones para la costa").

- **Base de datos**: tablas para snapshots de Open-Meteo; `recomendaciones` (recomendación puntual); `recomendaciones_horarias` (recomendación por hora para un día, para dashboards en Grafana).

## Para el evaluador (quick start)

1. **Clonar/copiar el proyecto** y entrar en la carpeta.
2. **Crear `.env`**: `cp .env.example .env` (los valores por defecto funcionan).
3. **Levantar el stack**: `docker compose up -d`.
4. **Generar datos para Grafana** (opcional; si no hay datos, los paneles pueden mostrar "No data"):
   ```bash
   for i in 0 1 2 3 4 5 6 7 8 9; do FECHA=$(date -d "+$i days" +%Y-%m-%d); curl -s "http://localhost:8001/api/recomendacion/horaria?fecha=$FECHA" > /dev/null; done
   ```
5. **Abrir**: API → http://localhost:8001/docs | Grafana → http://localhost:3000 (usuario `admin`, contraseña `admin`). Dashboard: **Actividades Costeras** → **Actividades Costeras A Coruña**.

Instrucciones detalladas: **[ENTREGA.md](ENTREGA.md)**.

## Requisitos

- Docker y Docker Compose.
- Copiar `.env.example` a `.env` (opcional: `LOCATION_ID` para etiquetado en BD).

## Cómo levantar el proyecto

```bash
cd /home/isma/Escritorio/Grafana
cp .env.example .env   # opcional: LOCATION_ID para registros en BD
docker compose up -d
```

- **PostgreSQL**: puerto **5433** en el host (5432 dentro del contenedor).
- **Grafana**: http://localhost:3000 (usuario `admin`, contraseña por defecto `admin`; configurable en `.env`).
- **Backend**: http://localhost:8001 (docs en http://localhost:8001/docs). Si en tu sistema el puerto 8001 está ocupado, puedes cambiar en `docker-compose.yml` el mapeo del backend (p. ej. a `8002:8000`).

## Uso de la API

- **Recomendación actual (score 1-10)**:
  ```bash
  curl http://localhost:8001/api/recomendacion
  ```
  Respuesta ejemplo:
  ```json
  {
    "score": 8,
    "explicacion": "Viento bajo (12 km/h), favorable para la costa. Oleaje bajo (0.3 m), favorable. Sin precipitación.",
    "wind_kmh": 12.0,
    "wave_height_m": 0.3,
    "precipitacion_mm": null,
    "mensaje": "Buenas condiciones para la costa."
  }
  ```

Cada llamada a `/api/recomendacion` obtiene datos actuales de Open-Meteo (viento, oleaje, precipitación), guarda snapshots en la BD, calcula el score, guarda una fila en `recomendaciones` y devuelve el resultado.

- **Recomendación por hora para un día (para Grafana)**:
  ```bash
  curl "http://localhost:8001/api/recomendacion/horaria?fecha=2026-02-28"
  ```
  Parámetros: `fecha` (obligatorio, YYYY-MM-DD; hoy o hasta 10 días futuros). Siempre para A Coruña.
  Respuesta: `fecha`, `ubicacion` (A Coruña) y `recomendaciones_por_hora`: lista de 24 entradas (una por hora) con `hora`, `score`, `wind_kmh`, `wave_height_m`, `precipitacion_mm`, `explicacion`, `mensaje`. Los datos se guardan en la tabla `recomendaciones_horarias` para consultas y gráficos en Grafana.

## Configuración (`.env`)

| Variable | Descripción |
|----------|-------------|
| `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` | Credenciales de PostgreSQL. Si cambias la contraseña, actualiza también `grafana/provisioning/datasources/datasources.yml` para que Grafana pueda conectar. |
| `GRAFANA_ADMIN_USER`, `GRAFANA_ADMIN_PASSWORD` | Usuario y contraseña de Grafana. |
| `LOCATION_ID` | Identificador de ubicación en BD (por defecto `a_coruna`). La app solo recomienda para A Coruña. |

## Estructura del proyecto

```
Grafana/
├── docker-compose.yml       # PostgreSQL + Grafana + backend (contenedores costa-*)
├── .env.example             # Plantilla; copiar a .env
├── ENTREGA.md               # Instrucciones para quien evalúa
├── LEVANTAR_STACK.md        # Paso 2 del proyecto
├── GENERAR_DATOS.md         # Paso 3: curls y comprobaciones
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── scripts/
│   │   ├── init_db.sql      # Tablas: openmeteo_snapshots, recomendaciones, recomendaciones_horarias
│   │   └── migrations/
│   └── app/
│       ├── main.py
│       ├── config.py
│       ├── database.py
│       ├── api/routes.py    # GET /api/recomendacion, /api/recomendacion/horaria, /api/health
│       ├── services/       # openmeteo, scoring (score 1-10)
│       └── repositories/
├── grafana/provisioning/
│   ├── datasources/datasources.yml   # PostgreSQL (base costa)
│   └── dashboards/
│       ├── dashboards.yml
│       └── costa-a-coruna.json       # Dashboard "Actividades Costeras A Coruña"
├── docs/                    # Guías Grafana y estado APIs
└── README.md
```

## Siguiente paso: Grafana (gráficos + alertas)

Hay un **dashboard de ejemplo** provisionado: al abrir Grafana (http://localhost:3000) verás la carpeta **Actividades Costeras** con el dashboard **Actividades Costeras A Coruña** (recomendación en el tiempo, viento/oleaje, tabla de últimas recomendaciones). Para tener datos que mostrar, llama antes a la API (p. ej. `curl http://localhost:8001/api/recomendacion` varias veces o programa un cron).

Guía detallada: **[docs/PASO_GRAFANA_DASHBOARDS_ALERTAS.md](docs/PASO_GRAFANA_DASHBOARDS_ALERTAS.md)** — consultas SQL útiles, cómo crear alertas (score &lt; 4, oleaje &gt; 2 m) y contact points.

## Otros pasos opcionales

- Frontend web que llame a `/api/recomendacion` y muestre el score.
- Job (cron/scheduler) que llame periódicamente a `/api/recomendacion` para ir llenando histórico.

## Licencia y atribución

- **Open-Meteo**: datos meteorológicos y marinos; uso según sus términos (https://open-meteo.com).
