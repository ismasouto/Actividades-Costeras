# Solución: base de datos "costa" no existe

## Causa

El volumen de PostgreSQL se creó la primera vez con usuario/BD **pesca**. Las variables `POSTGRES_USER` y `POSTGRES_DB` solo se usan al **inicializar un volumen vacío**; después, aunque cambies el `.env` a `costa`, el contenedor sigue usando los datos antiguos (usuario y BD `pesca`). Por eso "costa" no existe.

## Solución (recrear el volumen y usar "costa")

Desde la carpeta del proyecto Grafana:

1. **Bajar el stack y eliminar los volúmenes de este proyecto** (solo los de Grafana; no afecta a ismagram ni reservas):

   ```bash
   cd /home/isma/Escritorio/Grafana
   docker compose down -v
   ```

   Se borrarán los datos de PostgreSQL y Grafana de este proyecto (tablas, dashboards guardados en Grafana, etc.).

2. **Asegúrate de que tu `.env` tiene**:

   ```
   POSTGRES_USER=costa
   POSTGRES_PASSWORD=costa_secret
   POSTGRES_DB=costa
   ```

3. **Levantar de nuevo**:

   ```bash
   docker compose up -d
   ```

   Espera ~30 segundos. Postgres creará el usuario `costa`, la base `costa` y ejecutará `init_db.sql`.

4. **Comprobar**:

   ```bash
   docker exec costa-postgres psql -U costa -d costa -c "\dt"
   ```

   Deberías ver las tablas `openmeteo_snapshots`, `recomendaciones`, `recomendaciones_horarias`.

Después de esto, la API, Grafana y DBeaver (localhost:5433, usuario `costa`, base `costa`) usarán la base "costa" correctamente.
