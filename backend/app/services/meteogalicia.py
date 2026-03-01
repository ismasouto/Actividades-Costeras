"""
Cliente para la API MeteoSIX v4 de MeteoGalicia (predicción numérica con token).

Documentación (guía v4, abr 2021): es.readkong.com/page/gu-a-de-la-api-del-meteosix-versi-n-v4-meteogalicia
URL base según la guía: https://servizos.meteogalicia.gal/apiv4/

NOTA: Si la API devuelve 404, es posible que el servicio apiv4 en servizos.meteogalicia.gal
haya sido desactivado o reubicado. En ese caso la app usa Open-Meteo como fallback.
Comprobar en https://www.meteogalicia.gal/web/modelos-numericos/meteosix si hay una API actual.
"""
import logging
import httpx
from typing import Any

API_V4_BASE = "https://servizos.meteogalicia.gal/apiv4"
logger = logging.getLogger(__name__)


def fetch_numeric_forecast_apiv4(
    api_key: str,
    lon: float,
    lat: float,
    start_time: str | None = None,
    end_time: str | None = None,
) -> dict[str, Any] | None:
    """
    Obtiene predicción numérica de la API MeteoSIX v4 (requiere API_KEY).
    coords en la API son longitud,latitud. Variables: viento, precipitación, altura de ola.
    Si se pasan start_time y end_time (formato yyyy-MM-ddTHH:mm:ss), se pide solo ese rango.
    """
    url = f"{API_V4_BASE}/getNumericForecastInfo"
    params: dict[str, Any] = {
        "coords": f"{lon},{lat}",
        "variables": "wind,precipitation_amount,significative_wave_height",
        "format": "application/json",
        "lang": "es",
        "tz": "Europe/Madrid",
        "API_KEY": api_key,
    }
    if start_time:
        params["startTime"] = start_time
    if end_time:
        params["endTime"] = end_time
    try:
        with httpx.Client(timeout=20.0) as client:
            r = client.get(url, params=params)
            r.raise_for_status()
            data = r.json()
    except httpx.HTTPStatusError as e:
        logger.warning("MeteoGalicia API HTTP error: %s %s", e.response.status_code, e.response.text[:200])
        return None
    except (httpx.RequestError, ValueError) as e:
        logger.warning("MeteoGalicia API request/json error: %s", e)
        return None
    if not data or "features" not in data or not data["features"]:
        return None
    feat = data["features"][0]
    if feat.get("exception"):
        return None
    return data


def _first_value(values: list[Any] | None) -> float | None:
    """Primer valor numérico no nulo en la lista (para variables por hora)."""
    if not values:
        return None
    for v in values:
        if v is not None and v != "":
            try:
                return float(v)
            except (TypeError, ValueError):
                continue
    return None


def extraer_de_apiv4(data: dict[str, Any] | None) -> dict[str, Any]:
    """
    Extrae wind_kmh, precipitacion_mm y wave_height_m del GeoJSON de getNumericForecastInfo.
    Estructura: features[0].properties.days[0].variables[] con name y values.
    wind en la API devuelve módulo (km/h) y dirección; tomamos el primer valor como módulo.
    """
    out = {"wind_kmh": None, "precipitacion_mm": None, "wave_height_m": None}
    try:
        if not data or "features" not in data or not data["features"]:
            return out
        feat = data["features"][0]
        if feat.get("exception"):
            return out
        props = feat.get("properties") or {}
        days = props.get("days")
        if not days or not isinstance(days, list):
            return out
        first_day = days[0]
        if not isinstance(first_day, dict):
            return out
        variables = first_day.get("variables")
        if not variables or not isinstance(variables, list):
            return out
        for var in variables:
            if not isinstance(var, dict):
                continue
            name = (var.get("name") or "").strip().lower()
            values = var.get("values")
            val = _first_value(values if isinstance(values, list) else None)
            if val is None:
                continue
            if "wind" in name:
                out["wind_kmh"] = val
            elif "precipitation" in name or "precipitacion" in name:
                out["precipitacion_mm"] = val
            elif "wave" in name or "ola" in name or "significative_wave" in name:
                out["wave_height_m"] = val
    except (KeyError, IndexError, TypeError) as e:
        logger.warning("extraer_de_apiv4: estructura inesperada (%s)", e)
    return out


def _value_at(values: list[Any] | None, index: int) -> float | None:
    """Valor numérico en el índice, o None si no existe o no es número."""
    if not values or index < 0 or index >= len(values):
        return None
    v = values[index]
    if v is None or v == "":
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def extraer_horario_apiv4(data: dict[str, Any] | None, fecha: str) -> list[dict[str, Any]]:
    """
    Extrae datos por hora para el día fecha (YYYY-MM-DD).
    Devuelve lista de dicts con hora_local (HH:00), wind_kmh, precipitacion_mm, wave_height_m.
    """
    out: list[dict[str, Any]] = []
    if not data or "features" not in data or not data["features"]:
        return out
    feat = data["features"][0]
    if feat.get("exception"):
        return out
    props = feat.get("properties") or {}
    days = props.get("days")
    if not days or not isinstance(days, list):
        return out
    wind_values: list[Any] = []
    precip_values: list[Any] = []
    wave_values: list[Any] = []
    for day in days:
        if not isinstance(day, dict):
            continue
        time_period = day.get("timePeriod") or {}
        begin = (time_period.get("begin") or {}).get("timeInstant") or ""
        if not str(begin).startswith(fecha):
            continue
        variables = day.get("variables")
        if not variables or not isinstance(variables, list):
            continue
        for var in variables:
            if not isinstance(var, dict):
                continue
            name = (var.get("name") or "").strip().lower()
            vals = var.get("values")
            if not isinstance(vals, list):
                continue
            if "wind" in name:
                wind_values = vals
            elif "precipitation" in name or "precipitacion" in name:
                precip_values = vals
            elif "wave" in name or "ola" in name or "significative_wave" in name:
                wave_values = vals
        break
    n = max(len(wind_values), len(precip_values), len(wave_values), 24)
    n = min(n, 24)
    for i in range(n):
        w = _value_at(wind_values, i)
        p = _value_at(precip_values, i)
        v = _value_at(wave_values, i)
        out.append({
            "hora_local": f"{i:02d}:00",
            "wind_kmh": w,
            "precipitacion_mm": p,
            "wave_height_m": v,
        })
    return out
