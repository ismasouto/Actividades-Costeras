-- Ejecutar solo si la BD se creó antes de añadir la recomendación horaria.
-- Ejemplo: psql -U costa -d costa -f 001_recomendaciones_horarias.sql

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
