# Paso 2: Levantar el stack

Ejecuta estos comandos **en tu terminal**, desde la carpeta del proyecto.

## 1. Levantar los contenedores

```bash
cd /home/isma/Escritorio/Grafana
docker compose up -d --build
```

- Si todo va bien, verás algo como: `Container costa-postgres  Started`, `Container costa-grafana  Started`, `Container costa-backend  Started`.
- Si falla el **build** del backend (permisos de Docker), prueba sin sandbox o con permisos de Docker para tu usuario:
  - `sudo usermod -aG docker $USER` (luego cierra sesión y vuelve a entrar), o
  - ejecuta `docker compose up -d --build` desde una terminal normal (fuera de Cursor).

## 2. Comprobar que los tres servicios están en marcha

```bash
docker compose ps
```

Deberías ver tres contenedores con estado **Up** (o **running**): `costa-postgres`, `costa-grafana`, `costa-backend`.

## 3. Migración (solo si la base de datos ya existía antes)

Ejecuta la migración **solo si** ya habías levantado el proyecto antes de que existiera la tabla `recomendaciones_horarias` (por ejemplo, si al entrar en Grafana o al llamar a la API horaria ves errores de “tabla no existe”):

```bash
docker compose exec -T postgres psql -U costa -d costa < backend/scripts/migrations/001_recomendaciones_horarias.sql
```

Si es la **primera vez** que levantas el stack, no hace falta: el script `init_db.sql` ya crea todas las tablas, incluida `recomendaciones_horarias`.

---

Cuando `docker compose ps` muestre los tres contenedores en marcha, el paso 2 está listo.
