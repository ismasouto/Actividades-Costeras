import json
import logging
from app.database import get_cursor

logger = logging.getLogger(__name__)


def _safe_json(obj: dict) -> str:
    """Serializa a JSON; si falla, devuelve un objeto mínimo para no romper el flujo."""
    try:
        return json.dumps(obj, default=str)
    except (TypeError, ValueError) as e:
        logger.warning("json.dumps falló (%s), guardando placeholder", e)
        return json.dumps({"error": "serialization_failed", "message": str(e)})


def guardar_meteogalicia(concello_id: str, payload: dict) -> None:
    with get_cursor() as cur:
        cur.execute(
            """
            INSERT INTO meteogalicia_snapshots (concello_id, payload)
            VALUES (%s, %s::jsonb)
            """,
            (concello_id, _safe_json(payload)),
        )


def guardar_openmeteo(lat: float, lon: float, payload: dict) -> None:
    with get_cursor() as cur:
        cur.execute(
            """
            INSERT INTO openmeteo_snapshots (latitude, longitude, payload)
            VALUES (%s, %s, %s::jsonb)
            """,
            (lat, lon, _safe_json(payload)),
        )


def guardar_recomendacion(
    concello_id: str,
    score: int,
    explicacion: str,
    wind_kmh: float | None,
    wave_height_m: float | None,
    precipitacion: float | None,
    source_meteogalicia: dict | None,
    source_openmeteo: dict | None,
) -> None:
    with get_cursor() as cur:
        cur.execute(
            """
            INSERT INTO recomendaciones
            (concello_id, score, explicacion, wind_kmh, wave_height_m, precipitacion, source_meteogalicia, source_openmeteo)
            VALUES (%s, %s, %s, %s, %s, %s, %s::jsonb, %s::jsonb)
            """,
            (
                concello_id,
                score,
                explicacion,
                wind_kmh,
                wave_height_m,
                precipitacion,
                _safe_json(source_meteogalicia or {}),
                _safe_json(source_openmeteo or {}),
            ),
        )


def guardar_recomendaciones_horarias(
    fecha: str,
    lat: float,
    lon: float,
    filas: list[tuple[int, int, float | None, float | None, float | None, str]],
) -> None:
    """
    Inserta filas en recomendaciones_horarias.
    filas: list of (hora_local 0-23, score, wind_kmh, wave_height_m, precipitacion_mm, explicacion).
    """
    with get_cursor() as cur:
        for hora_local, score, wind_kmh, wave_height_m, precipitacion_mm, explicacion in filas:
            cur.execute(
                """
                INSERT INTO recomendaciones_horarias
                (fecha, hora_local, latitude, longitude, score, wind_kmh, wave_height_m, precipitacion_mm, explicacion)
                VALUES (%s::date, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (fecha, hora_local, lat, lon, score, wind_kmh, wave_height_m, precipitacion_mm, explicacion or ""),
            )
