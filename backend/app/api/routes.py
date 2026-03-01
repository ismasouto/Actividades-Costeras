"""
Rutas API: recomendación actual (score 1-10) y recomendación horaria por día.
Ambas para A Coruña; datos de Open-Meteo (viento, oleaje, precipitación).
"""
import logging
from datetime import date, timedelta

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.config import get_settings, A_CORUNA_LAT, A_CORUNA_LON

logger = logging.getLogger(__name__)
from app.services import openmeteo
from app.services.scoring import calcular_score, preparar_fuentes_para_score
from app.repositories import recomendaciones as repo

router = APIRouter(prefix="/api", tags=["api"])


class RecomendacionHora(BaseModel):
    hora: str
    score: int
    wind_kmh: float | None
    wave_height_m: float | None
    precipitacion_mm: float | None
    explicacion: str
    mensaje: str


class RecomendacionHorariaResponse(BaseModel):
    fecha: str
    ubicacion: dict
    recomendaciones_por_hora: list[RecomendacionHora]


class RecomendacionResponse(BaseModel):
    score: int
    explicacion: str
    wind_kmh: float | None
    wave_height_m: float | None
    precipitacion_mm: float | None
    mensaje: str


def _mensaje_para_score(score: int) -> str:
    if score >= 9:
        return "Condiciones excelentes para actividades costeras."
    if score >= 7:
        return "Buenas condiciones para la costa."
    if score >= 5:
        return "Condiciones aceptables; ten en cuenta viento y oleaje."
    if score >= 3:
        return "No muy recomendable; valora el riesgo."
    return "Desaconsejado por condiciones adversas o peligrosas."


@router.get("/recomendacion", response_model=RecomendacionResponse)
def get_recomendacion():
    """
    Recomendación actual para actividades costeras en A Coruña: puntuación 1-10 y explicación.
    Motor: Open-Meteo (viento, oleaje, precipitación). Ubicación fija: A Coruña.
    """
    try:
        settings = get_settings()
        location_id = settings.location_id
        lat, lon = A_CORUNA_LAT, A_CORUNA_LON

        weather = openmeteo.fetch_weather(lat, lon)
        marine = openmeteo.fetch_marine(lat, lon)
        om_extract = openmeteo.extraer_oleaje(marine)

        mg_extract = {}
        if weather and "current" in weather:
            c = weather["current"]
            mg_extract["wind_kmh"] = c.get("wind_speed_10m")
            mg_extract["precipitacion_mm"] = c.get("precipitation")
        if marine:
            repo.guardar_openmeteo(lat, lon, marine)

        wind, wave, precip = preparar_fuentes_para_score(mg_extract, om_extract)
        score, explicacion = calcular_score(wind, wave, precip)

        repo.guardar_recomendacion(
            concello_id=location_id,
            score=score,
            explicacion=explicacion,
            wind_kmh=wind,
            wave_height_m=wave,
            precipitacion=precip,
            source_meteogalicia={},
            source_openmeteo={
                "marine": marine is not None,
                "wave_height_m": om_extract.get("wave_height_m"),
                "wave_period_s": om_extract.get("wave_period_s"),
            },
        )

        return RecomendacionResponse(
            score=int(score),
            explicacion=explicacion,
            wind_kmh=wind,
            wave_height_m=wave,
            precipitacion_mm=precip,
            mensaje=_mensaje_para_score(score),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error en get_recomendacion: %s", e)
        raise HTTPException(
            status_code=503,
            detail=f"Error al obtener o guardar la recomendación: {e!s}",
        )


@router.get("/recomendacion/horaria", response_model=RecomendacionHorariaResponse)
def get_recomendacion_horaria(
    fecha: date = Query(..., description="Día deseado (YYYY-MM-DD). Hoy o días futuros."),
):
    """
    Recomendación para actividades costeras por hora en A Coruña (Open-Meteo).
    Devuelve un valor 1-10 por cada hora del día. Ubicación fija: A Coruña.
    """
    lat, lon = A_CORUNA_LAT, A_CORUNA_LON
    hoy = date.today()
    if fecha < hoy:
        raise HTTPException(status_code=400, detail="La fecha no puede ser anterior a hoy.")
    if fecha > hoy + timedelta(days=10):
        raise HTTPException(status_code=400, detail="La fecha no puede ser más de 10 días en el futuro.")

    fecha_str = fecha.isoformat()

    try:
        weather_hourly = openmeteo.fetch_weather_hourly(lat, lon, fecha_str, fecha_str)
        marine_hourly = openmeteo.fetch_marine_hourly(lat, lon, fecha_str, fecha_str)
        om_wind, om_precip = openmeteo.extraer_horario_weather(weather_hourly, fecha_str)
        om_wave = openmeteo.extraer_horario_marine(marine_hourly, fecha_str)

        recomendaciones_por_hora = []
        filas_para_bd = []

        for hora in range(24):
            wind = om_wind[hora] if hora < len(om_wind) else None
            precip = om_precip[hora] if hora < len(om_precip) else None
            wave = om_wave[hora] if hora < len(om_wave) else None

            score, explicacion = calcular_score(wind, wave, precip)
            mensaje = _mensaje_para_score(score)
            recomendaciones_por_hora.append(
                RecomendacionHora(
                    hora=f"{hora:02d}:00",
                    score=score,
                    wind_kmh=wind,
                    wave_height_m=wave,
                    precipitacion_mm=precip,
                    explicacion=explicacion,
                    mensaje=mensaje,
                )
            )
            filas_para_bd.append((hora, score, wind, wave, precip, explicacion))

        repo.guardar_recomendaciones_horarias(fecha_str, lat, lon, filas_para_bd)

        return RecomendacionHorariaResponse(
            fecha=fecha_str,
            ubicacion={"lat": lat, "lon": lon},
            recomendaciones_por_hora=recomendaciones_por_hora,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error en get_recomendacion_horaria: %s", e)
        raise HTTPException(
            status_code=503,
            detail=f"Error al obtener recomendación horaria: {e!s}",
        )


@router.get("/health")
def health():
    return {"status": "ok"}
