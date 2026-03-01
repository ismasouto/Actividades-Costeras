"""
Cliente Open-Meteo: motor del score para actividades costeras.
- Weather API: viento (wind_speed_10m) y precipitación.
- Marine API: oleaje (wave_height, wave_period).
Documentación: https://open-meteo.com/en/docs/marine-weather-api
"""
import httpx
from typing import Any

MARINE_BASE = "https://marine-api.open-meteo.com/v1/marine"
WEATHER_BASE = "https://api.open-meteo.com/v1/forecast"


def fetch_marine(lat: float, lon: float) -> dict[str, Any] | None:
    """Oleaje actual: wave_height (m), wave_period, wind_wave_height, swell_wave_height."""
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "wave_height,wave_period,wind_wave_height,swell_wave_height",
        "timezone": "Europe/Madrid",
    }
    with httpx.Client(timeout=15.0) as client:
        r = client.get(MARINE_BASE, params=params)
        r.raise_for_status()
        return r.json()


def fetch_weather(lat: float, lon: float) -> dict[str, Any] | None:
    """Viento actual a 10 m y precipitación (km/h, mm)."""
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "wind_speed_10m,wind_direction_10m,precipitation",
        "timezone": "Europe/Madrid",
    }
    with httpx.Client(timeout=15.0) as client:
        r = client.get(WEATHER_BASE, params=params)
        r.raise_for_status()
        return r.json()


def extraer_oleaje(marine: dict | None) -> dict[str, Any]:
    """Extrae wave_height (m) y datos relacionados para el score."""
    out = {"wave_height_m": None, "wave_period_s": None, "raw": marine}
    if not marine or "current" not in marine:
        return out
    c = marine["current"]
    out["wave_height_m"] = c.get("wave_height")
    out["wave_period_s"] = c.get("wave_period")
    return out


def fetch_weather_hourly(lat: float, lon: float, start_date: str, end_date: str) -> dict[str, Any] | None:
    """Predicción horaria: viento y precipitación entre start_date y end_date (YYYY-MM-DD)."""
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "wind_speed_10m,precipitation",
        "timezone": "Europe/Madrid",
        "start_date": start_date,
        "end_date": end_date,
    }
    with httpx.Client(timeout=15.0) as client:
        r = client.get(WEATHER_BASE, params=params)
        r.raise_for_status()
        return r.json()


def fetch_marine_hourly(lat: float, lon: float, start_date: str, end_date: str) -> dict[str, Any] | None:
    """Predicción horaria de oleaje entre start_date y end_date (YYYY-MM-DD)."""
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "wave_height",
        "timezone": "Europe/Madrid",
        "start_date": start_date,
        "end_date": end_date,
    }
    with httpx.Client(timeout=15.0) as client:
        r = client.get(MARINE_BASE, params=params)
        r.raise_for_status()
        return r.json()


def extraer_horario_weather(hourly_data: dict[str, Any] | None, fecha: str) -> tuple[list[float | None], list[float | None]]:
    """
    Extrae listas por hora para wind_speed_10m y precipitation del día fecha.
    Devuelve (wind_kmh_por_hora, precip_por_hora), cada una de longitud 24.
    """
    wind = [None] * 24
    precip = [None] * 24
    if not hourly_data or "hourly" not in hourly_data:
        return (wind, precip)
    h = hourly_data["hourly"]
    times = h.get("time") or []
    wind_list = h.get("wind_speed_10m") or []
    precip_list = h.get("precipitation") or []
    for i, t in enumerate(times):
        if not str(t).startswith(fecha):
            continue
        try:
            hour = int(str(t)[11:13])
        except (ValueError, IndexError):
            continue
        if 0 <= hour < 24:
            wind[hour] = wind_list[i] if i < len(wind_list) else None
            precip[hour] = precip_list[i] if i < len(precip_list) else None
    return (wind, precip)


def extraer_horario_marine(hourly_data: dict[str, Any] | None, fecha: str) -> list[float | None]:
    """Extrae wave_height por hora para el día fecha (lista de 24 elementos)."""
    wave = [None] * 24
    if not hourly_data or "hourly" not in hourly_data:
        return wave
    h = hourly_data["hourly"]
    times = h.get("time") or []
    wave_list = h.get("wave_height") or []
    for i, t in enumerate(times):
        if not str(t).startswith(fecha):
            continue
        try:
            hour = int(str(t)[11:13])
        except (ValueError, IndexError):
            continue
        if 0 <= hour < 24 and i < len(wave_list):
            wave[hour] = wave_list[i]
    return wave
