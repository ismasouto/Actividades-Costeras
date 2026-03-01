-- Inicialización de la base de datos para Actividades Costeras (Reto Grafana HACKUDC 2026).
-- Se ejecuta automáticamente la primera vez que el contenedor PostgreSQL arranca.

-- Datos crudos de MeteoGalicia (predicción/observación por concello)
CREATE TABLE IF NOT EXISTS meteogalicia_snapshots (
    id          SERIAL PRIMARY KEY,
    fetched_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    concello_id VARCHAR(20) NOT NULL,
    payload     JSONB
);

-- Datos crudos de Open-Meteo (oleaje y viento marino)
CREATE TABLE IF NOT EXISTS openmeteo_snapshots (
    id          SERIAL PRIMARY KEY,
    fetched_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    latitude    NUMERIC(9,6) NOT NULL,
    longitude   NUMERIC(9,6) NOT NULL,
    payload     JSONB
);

-- Recomendación calculada: puntuación 1-10 y explicación
CREATE TABLE IF NOT EXISTS recomendaciones (
    id           SERIAL PRIMARY KEY,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    concello_id  VARCHAR(20) NOT NULL,
    score        SMALLINT NOT NULL CHECK (score >= 1 AND score <= 10),
    explicacion  TEXT,
    -- Resumen de variables usadas para el score (para Grafana y auditoría)
    wind_kmh     NUMERIC(6,2),
    wave_height_m NUMERIC(5,2),
    precipitacion NUMERIC(6,2),
    source_meteogalicia JSONB,
    source_openmeteo   JSONB
);

-- Recomendación por hora para un día (para Grafana y endpoint horario)
CREATE TABLE IF NOT EXISTS recomendaciones_horarias (
    id            SERIAL PRIMARY KEY,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    fecha         DATE NOT NULL,
    hora_local    SMALLINT NOT NULL CHECK (hora_local >= 0 AND hora_local <= 23),
    latitude      NUMERIC(9,6) NOT NULL,
    longitude     NUMERIC(9,6) NOT NULL,
    score         SMALLINT NOT NULL CHECK (score >= 1 AND score <= 10),
    wind_kmh      NUMERIC(6,2),
    wave_height_m NUMERIC(5,2),
    precipitacion_mm NUMERIC(6,2),
    explicacion   TEXT
);

CREATE INDEX IF NOT EXISTS idx_recomendaciones_horarias_fecha ON recomendaciones_horarias(fecha);
CREATE INDEX IF NOT EXISTS idx_recomendaciones_horarias_fecha_hora ON recomendaciones_horarias(fecha, hora_local);

CREATE INDEX IF NOT EXISTS idx_recomendaciones_created_at ON recomendaciones(created_at);
CREATE INDEX IF NOT EXISTS idx_recomendaciones_concello ON recomendaciones(concello_id);
CREATE INDEX IF NOT EXISTS idx_meteogalicia_fetched ON meteogalicia_snapshots(fetched_at);
CREATE INDEX IF NOT EXISTS idx_openmeteo_fetched ON openmeteo_snapshots(fetched_at);
