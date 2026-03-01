"""
Lógica de puntuación 1-10 para actividades costeras (condiciones en la costa).
Fuente: Open-Meteo (viento, oleaje, precipitación).
Cuanto más bajo el viento y oleaje y sin lluvia, mayor puntuación.
"""
from typing import Any


def calcular_score(
    wind_kmh: float | None,
    wave_height_m: float | None,
    precipitacion_mm: float | None,
) -> tuple[int, str]:
    """
    Devuelve (score 1-10, explicación).
    Criterios orientativos (se pueden afinar):
    - Viento: < 15 km/h ideal, 15-30 aceptable, 30-50 malo, > 50 peligroso
    - Oleaje: < 0.5 m ideal, 0.5-1.5 aceptable, 1.5-2.5 malo, > 2.5 peligroso
    - Precipitación: 0 ideal, > 0 resta
    """
    puntos = 10.0
    razones = []

    # Viento (peso alto para actividades costeras)
    if wind_kmh is not None:
        if wind_kmh > 50:
            puntos -= 5
            razones.append(f"Viento muy fuerte ({wind_kmh:.0f} km/h), riesgo alto.")
        elif wind_kmh > 30:
            puntos -= 2.5
            razones.append(f"Viento fuerte ({wind_kmh:.0f} km/h).")
        elif wind_kmh > 15:
            puntos -= 1
            razones.append(f"Viento moderado ({wind_kmh:.0f} km/h).")
        else:
            razones.append(f"Viento bajo ({wind_kmh:.0f} km/h), favorable para la costa.")
    else:
        razones.append("Sin dato de viento.")

    # Oleaje
    if wave_height_m is not None:
        if wave_height_m > 2.5:
            puntos -= 4
            razones.append(f"Oleaje muy alto ({wave_height_m:.1f} m), peligroso.")
        elif wave_height_m > 1.5:
            puntos -= 2
            razones.append(f"Oleaje alto ({wave_height_m:.1f} m).")
        elif wave_height_m > 0.5:
            puntos -= 0.5
            razones.append(f"Oleaje moderado ({wave_height_m:.1f} m).")
        else:
            razones.append(f"Oleaje bajo ({wave_height_m:.1f} m), favorable.")
    else:
        razones.append("Sin dato de oleaje.")

    # Precipitación
    if precipitacion_mm is not None and precipitacion_mm > 0:
        if precipitacion_mm > 5:
            puntos -= 2
            razones.append(f"Precipitación significativa ({precipitacion_mm:.1f} mm).")
        else:
            puntos -= 0.5
            razones.append(f"Algo de precipitación ({precipitacion_mm:.1f} mm).")
    elif precipitacion_mm is not None:
        razones.append("Sin precipitación.")

    score = max(1, min(10, round(puntos)))
    explicacion = " ".join(razones)
    return score, explicacion


def preparar_fuentes_para_score(
    weather_extract: dict[str, Any],
    openmeteo_extract: dict[str, Any],
) -> tuple[float | None, float | None, float | None]:
    """Extrae wind_kmh, wave_height_m, precipitacion_mm de Open-Meteo (weather + marine)."""
    wind = weather_extract.get("wind_kmh")
    if wind is not None:
        wind = float(wind)
    wave = openmeteo_extract.get("wave_height_m")
    if wave is not None:
        wave = float(wave)
    precip = weather_extract.get("precipitacion_mm")
    if precip is not None:
        precip = float(precip)
    return wind, wave, precip
