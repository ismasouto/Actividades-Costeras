# Paso 3: Generar datos en la base de datos

Para que Grafana pueda mostrar recomendaciones, las tablas `recomendaciones` y `recomendaciones_horarias` tienen que tener al menos algunas filas. Eso se consigue llamando a la API.

## 1. Recomendación actual (una fila en `recomendaciones`)

En una terminal:

```bash
curl http://localhost:8001/api/recomendacion
```

- Si todo va bien: verás un JSON con `score`, `explicacion`, `wind_kmh`, `wave_height_m`, `precipitacion_mm`, `mensaje`.
- Si ves **503** ("METEOGALICIA_API_KEY no está configurada"): añade tu token en el `.env` en la línea `METEOGALICIA_API_KEY=...`, guarda, y reinicia el backend:  
  `docker compose restart backend`  
  Luego vuelve a ejecutar el `curl`.
- Si ves **500 Internal Server Error**: revisa los logs del backend para ver el motivo:  
  `docker compose logs backend --tail 50`

## 2. Recomendación por horas de un día (24 filas en `recomendaciones_horarias`)

Sustituye `YYYY-MM-DD` por **hoy** o **mañana** (por ejemplo `2026-03-01`):

```bash
curl "http://localhost:8001/api/recomendacion/horaria?fecha=YYYY-MM-DD"
```

Ejemplo para mañana:

```bash
curl "http://localhost:8001/api/recomendacion/horaria?fecha=2026-03-01"
```

- Si va bien: recibirás un JSON con `fecha`, `ubicacion` y `recomendaciones_por_hora` (lista de 24 horas con `score`, etc.).
- Si falla (503, 500): mismo criterio que arriba (revisar `.env`, reiniciar backend, mirar `docker compose logs backend`).

## 3. Comprobar que hay datos en la base de datos (opcional)

Si tienes `psql` o un cliente PostgreSQL, puedes conectar a la BD del proyecto (puerto **5433** en el host, usuario `costa`, base `costa`) y ejecutar:

```sql
SELECT COUNT(*) FROM recomendaciones;
SELECT COUNT(*) FROM recomendaciones_horarias;
```

O, desde Docker:

```bash
docker compose exec postgres psql -U costa -d costa -c "SELECT COUNT(*) FROM recomendaciones;"
docker compose exec postgres psql -U costa -d costa -c "SELECT COUNT(*) FROM recomendaciones_horarias;"
```

Si ambos números son al menos 1 (y 24 en la horaria tras el segundo curl), el paso 3 está listo para seguir con Grafana.
