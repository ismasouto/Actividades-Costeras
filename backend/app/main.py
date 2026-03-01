"""
API Actividades Costeras: recomendación 1-10 para condiciones en la costa (A Coruña).
Expone /api/recomendacion y /api/recomendacion/horaria; datos en PostgreSQL; visualización en Grafana.
"""
import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")

app = FastAPI(
    title="Actividades Costeras – Recomendación 1-10 (A Coruña)",
    description="API para recomendar condiciones para actividades costeras en A Coruña. Puntuación 1-10 con Open-Meteo (viento, oleaje, precipitación). Ubicación fija: A Coruña.",
    version="0.1.0",
)


@app.exception_handler(Exception)
def _unhandled_exception(request, exc):
    """Evita 500: cualquier error no manejado se devuelve como 503 con detalle."""
    from fastapi.responses import JSONResponse
    from fastapi.exceptions import RequestValidationError
    if isinstance(exc, HTTPException):
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
    if isinstance(exc, RequestValidationError):
        raise exc  # deja que FastAPI devuelva 422
    logging.getLogger(__name__).exception("Excepción no manejada: %s", exc)
    return JSONResponse(
        status_code=503,
        content={"detail": f"Error interno: {exc!s}"},
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)


@app.get("/")
def root():
    return {
        "message": "API Actividades Costeras – Reto Grafana HACKUDC 2026",
        "ubicacion": "A Coruña (fija)",
        "docs": "/docs",
        "recomendacion": "GET /api/recomendacion",
        "recomendacion_horaria": "GET /api/recomendacion/horaria?fecha=YYYY-MM-DD",
    }
