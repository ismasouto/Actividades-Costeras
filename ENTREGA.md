# Instrucciones para el evaluador

Proyecto **Actividades Costeras – Reto Grafana HACKUDC 2026**: recomendación 1-10 para condiciones en la costa (A Coruña) con Open-Meteo y visualización en Grafana.

---

## Requisitos

- **Docker** y **Docker Compose** instalados.
- Puertos libres: **5433** (PostgreSQL en el host), **3000** (Grafana), **8001** (API).

---

## Pasos para probar el proyecto

### 1. Preparar el entorno

En la raíz del proyecto (donde está `docker-compose.yml`):

```bash
cp .env.example .env
```

No es obligatorio editar `.env`; los valores por defecto permiten probar todo (usuario/BD `costa`, contraseña `costa_secret`, Grafana `admin`/`admin`).

### 2. Levantar el stack

```bash
docker compose up -d
```

Esperar unos 20–30 segundos a que PostgreSQL pase el healthcheck y arranquen Grafana y el backend. Comprobar:

```bash
docker compose ps
```

Los tres contenedores (`costa-postgres`, `costa-grafana`, `costa-backend`) deben estar en estado **Up**.

### 3. Comprobar la API

- **Documentación interactiva**: http://localhost:8001/docs  
- **Recomendación actual**:  
  ```bash
  curl http://localhost:8001/api/recomendacion
  ```  
  Debe devolver un JSON con `score`, `explicacion`, `wind_kmh`, `wave_height_m`, `mensaje`.

- **Recomendación horaria** (un día):  
  ```bash
  curl "http://localhost:8001/api/recomendacion/horaria?fecha=$(date +%Y-%m-%d)"
  ```  
  Debe devolver `recomendaciones_por_hora` con 24 entradas.

### 4. Generar datos para los dashboards (opcional)

Para que Grafana muestre gráficos con datos, hay que insertar recomendaciones horarias. Por ejemplo, **10 días** (hoy + 9):

**Linux:**

```bash
for i in 0 1 2 3 4 5 6 7 8 9; do
  FECHA=$(date -d "+$i days" +%Y-%m-%d)
  echo "Generando $FECHA..."
  curl -s "http://localhost:8001/api/recomendacion/horaria?fecha=$FECHA" > /dev/null
done
```

**macOS:**

```bash
for i in 0 1 2 3 4 5 6 7 8 9; do
  FECHA=$(date -v+${i}d +%Y-%m-%d)
  echo "Generando $FECHA..."
  curl -s "http://localhost:8001/api/recomendacion/horaria?fecha=$FECHA" > /dev/null
done
```

### 5. Abrir Grafana

- **URL**: http://localhost:3000  
- **Usuario**: `admin`  
- **Contraseña**: `admin` (o la definida en `GRAFANA_ADMIN_PASSWORD` en `.env`)

En el menú: **Dashboards** → carpeta **Actividades Costeras** → dashboard **Actividades Costeras A Coruña**.  
Si en el paso 4 se generaron datos, los paneles mostrarán series temporales y tabla. Si no, pueden aparecer vacíos o "No data" (el dashboard está correctamente configurado para leer de `recomendaciones_horarias` cuando se editan las consultas en la UI; el JSON de provisioning puede usar `recomendaciones` por defecto).

### 6. Bajar el stack (al terminar)

```bash
docker compose down
```

Para borrar también los datos (volúmenes):

```bash
docker compose down -v
```

---

## Resumen de URLs y credenciales

| Servicio   | URL / Acceso |
|-----------|---------------|
| API (docs)| http://localhost:8001/docs |
| API (raíz)| http://localhost:8001/ |
| Grafana   | http://localhost:3000 (usuario `admin`, contraseña `admin`) |
| PostgreSQL (desde el host) | Puerto **5433**, usuario `costa`, base `costa`, contraseña `costa_secret` |

---

## Frases para la defensa (resumen del proyecto)

- **Qué hace**: "El proyecto da una **recomendación del 1 al 10** para **actividades costeras en A Coruña** según viento, oleaje y precipitación (Open-Meteo). Los datos se guardan en PostgreSQL y se visualizan en Grafana."
- **Cómo se levanta**: "Con **Docker Compose**: solo hace falta copiar `.env.example` a `.env` y ejecutar `docker compose up -d`. La API está en el puerto 8001 y Grafana en el 3000."
- **Datos**: "Usamos **Open-Meteo** (Weather + Marine) sin API key. La ubicación es fija: A Coruña. Hay dos endpoints: recomendación actual y recomendación por hora para un día, que rellena la tabla para los dashboards."
- **Grafana**: "Hay un dashboard provisionado, **Actividades Costeras A Coruña**, con gráficos de score, viento y oleaje, y una tabla de últimas recomendaciones. Las alertas se pueden configurar desde el propio Grafana (por ejemplo score bajo u oleaje alto)."

---

## Para el autor (antes de entregar)

1. **Comprobar que `.env` no se sube**: `git status` — `.env` no debe aparecer (está en `.gitignore`).
2. **Probar desde cero** en otra carpeta o tras `docker compose down -v`: copiar `.env.example` a `.env`, `docker compose up -d`, generar datos (curls horarios), abrir Grafana y revisar el dashboard.
3. **Revisar que no haya secretos** en el repo (solo `.env.example` con valores de ejemplo).
4. **Si usas Git**: hacer commit de los últimos cambios y, si aplica, crear un tag de entrega (p. ej. `git tag v1.0-entrega`) y entregar ese commit/tag.
