# Siguiente paso: representación gráfica (Grafana) + alertas

Objetivo: ver en Grafana los datos de recomendación para actividades costeras en A Coruña y recibir alertas cuando las condiciones sean malas.

---

## Resumen del flujo

1. **Tener datos en la BD** → el backend escribe en `recomendaciones` y `recomendaciones_horarias` cuando llamas a la API.
2. **Grafana ya está conectada** al PostgreSQL (datasource "PostgreSQL" provisionado).
3. **Falta**: crear **dashboards** (paneles que consulten esas tablas) y **alertas** (ej. aviso si score &lt; 4 u oleaje &gt; 2 m).

---

## Paso 1: Generar datos en la BD (si aún no hay)

Para que los gráficos tengan qué mostrar, genera al menos unas cuantas filas:

```bash
# Recomendación actual (una fila en recomendaciones)
curl http://localhost:8001/api/recomendacion

# Recomendación horaria para hoy (24 filas en recomendaciones_horarias)
curl "http://localhost:8001/api/recomendacion/horaria?fecha=$(date +%Y-%m-%d)"
```

Repite varias veces o programa un cron que llame a `/api/recomendacion` cada X minutos para tener serie temporal.

---

## Paso 2: Entrar en Grafana y abrir el dashboard

1. Abre **http://localhost:3000** e inicia sesión (por defecto `admin` / `admin`).
2. Menú lateral → **Dashboards** → abrir la carpeta **Actividades Costeras** (o el dashboard **Actividades Costeras A Coruña** si está provisionado).
3. Si has añadido el dashboard provisionado de este repo, verás:
   - **Score en el tiempo**: evolución del score 1–10 (tabla `recomendaciones`).
   - **Viento y oleaje**: series de `wind_kmh` y `wave_height_m`.
   - **Últimas recomendaciones**: tabla con las filas recientes.
   - **Recomendación por hora** (opcional): score por hora del día en `recomendaciones_horarias`.

---

## Paso 3: Crear o editar paneles (consultas útiles)

Datasource: **PostgreSQL**.

### Serie temporal del score (tabla `recomendaciones`)

```sql
SELECT created_at AS time, score
FROM recomendaciones
WHERE created_at >= $__timeFrom() AND created_at <= $__timeTo()
ORDER BY created_at;
```

- Tipo de panel: **Time series** (o Graph).
- En "Format as": **Time series** (time en el eje X).

### Viento y oleaje en el tiempo

```sql
SELECT created_at AS time, wind_kmh AS "Viento (km/h)", wave_height_m AS "Oleaje (m)"
FROM recomendaciones
WHERE created_at >= $__timeFrom() AND created_at <= $__timeTo()
ORDER BY created_at;
```

- Tipo: **Time series** con dos series (Viento y Oleaje).

### Tabla de últimas recomendaciones

```sql
SELECT created_at AS "Fecha", score AS "Score", wind_kmh AS "Viento km/h",
       wave_height_m AS "Oleaje m", precipitacion AS "Precip. mm", explicacion AS "Explicación"
FROM recomendaciones
ORDER BY created_at DESC
LIMIT 20;
```

- Tipo de panel: **Table**.

### Score por hora de un día (`recomendaciones_horarias`)

Usa una variable de dashboard `fecha` (tipo date) o fija una fecha:

```sql
SELECT hora_local AS "Hora", score AS "Score", wind_kmh AS "Viento km/h",
       wave_height_m AS "Oleaje m", precipitacion_mm AS "Precip. mm"
FROM recomendaciones_horarias
WHERE fecha = $__timeFilter(fecha) OR fecha = '2026-02-28'  -- ajusta o usa variable
ORDER BY hora_local;
```

O con filtro por fecha desde el dashboard:

```sql
SELECT hora_local AS "Hora", score, wind_kmh, wave_height_m, precipitacion_mm
FROM recomendaciones_horarias
WHERE fecha = '$fecha'
ORDER BY hora_local;
```

(creando una variable `fecha` de tipo **Query** con algo como `SELECT DISTINCT fecha::text FROM recomendaciones_horarias ORDER BY 1 DESC LIMIT 30`).

---

## Paso 4: Configurar alertas

En Grafana 9+ las alertas unificadas se configuran desde un panel o desde **Alerting** → **Alert rules**.

### Opción A: alerta desde un panel (Time series del score)

1. Edita el panel del **score en el tiempo**.
2. Pestaña **Alert** → **Create alert rule from this panel**.
3. Condición: por ejemplo **when avg() of (A) is below 4** (score bajo = malas condiciones).
4. Añade **Contact points** (notificaciones): en **Alerting** → **Contact points** configura un canal (email, Slack, etc.) y asígnalo al rule.

### Opción B: alerta por oleaje alto

1. Panel con serie `wave_height_m`.
2. Crear regla: **when max() of (A) is above 2** (oleaje &gt; 2 m = peligroso).
3. Asignar contact point.

### Resumen de umbrales sugeridos

| Alerta        | Condición (ejemplo) | Interpretación              |
|---------------|----------------------|-----------------------------|
| Score bajo    | avg(score) &lt; 4     | Condiciones desaconsejadas  |
| Oleaje alto   | max(wave_height_m) &gt; 2 | Riesgo por oleaje      |
| Viento fuerte | max(wind_kmh) &gt; 40 | Riesgo por viento           |

---

## Estructura de provisioning en este proyecto

```
grafana/provisioning/
├── datasources/
│   └── datasources.yml          # PostgreSQL (ya existe)
└── dashboards/
    └── dashboards.yml           # Proveedor que carga JSON de esta carpeta
    └── costa-a-coruna.json (dashboard "Actividades Costeras A Coruña")      # Dashboard de ejemplo (si se añade)
```

Tras añadir o modificar JSON en `provisioning/dashboards/`, reinicia Grafana o espera al refresh del proveedor para que cargue los cambios.

---

## Checklist rápido

- [ ] Stack levantado: `docker compose up -d`
- [ ] Datos en BD: al menos unas llamadas a `/api/recomendacion` y `/api/recomendacion/horaria`
- [ ] Grafana: login en http://localhost:3000
- [ ] Dashboard "Actividades Costeras A Coruña" visible (si está provisionado) o creado a mano con las consultas de arriba
- [ ] Una o más alertas creadas (score bajo u oleaje alto) con contact point configurado

Cuando tengas el dashboard base, puedes refinar intervalos, variables (p. ej. elegir día) y más alertas según el reto.
