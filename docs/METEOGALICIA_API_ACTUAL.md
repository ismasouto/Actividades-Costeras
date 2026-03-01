# Estado de las APIs de MeteoGalicia (comprobado en web)

## Resumen

- **API MeteoSIX v4** (`servizos.meteogalicia.gal/apiv4/getNumericForecastInfo`): responde **404**. La guía es de abril de 2021; ese endpoint ya no está disponible (o ha sido reubicado).
- **APIs en `servizos.meteogalicia.gal/mgrss/`**: **sí funcionan**, sin clave API.

---

## APIs que SÍ funcionan (sin API_KEY)

Base: `https://servizos.meteogalicia.gal/mgrss/`

| Servicio | URL | Uso |
|----------|-----|-----|
| **Predicción por concello (JSON)** | `predicion/jsonPredConcellos.action?idConc={idConc}` | Predicción por días (temperatura, probabilidad de lluvia, viento dirección, cielo). No da viento en km/h ni oleaje hora a hora. |
| **Observación por concello** | `observacion/observacionConcellos.action?idConcello={id}` | Datos de observación del concello. |
| **Lista estaciones** | `observacion/listaEstacionsMeteo.action` | Listado de estaciones meteorológicas. |
| **Datos diarios estación** | `observacion/datosDiariosEstacionsMeteo.action?idEst={id}` | Datos diarios por estación. |
| **Últimos 10 min estación** | `observacion/ultimos10minEstacionsMeteo.action?idEst={id}` | Datos recientes por estación. |
| **Mareas (RSS)** | `predicion/rssMareas.action?idPorto={id}&dataIni={dd/mm/yyyy}&dataFin={dd/mm/yyyy}` | Predicción de mareas. |

Ejemplo de predicción por concello (A Coruña, id 15030):

```bash
curl "https://servizos.meteogalicia.gal/mgrss/predicion/jsonPredConcellos.action?idConc=15030"
```

Respuesta: `predConcello` con `listaPredDiaConcello` (días con `dataPredicion`, `tMax`, `tMin`, `pchoiva`, `vento` [dirección en grados], `ceo`, etc.). No incluye velocidad del viento en km/h ni altura de ola por hora.

---

## API v4 (getNumericForecastInfo) – no disponible

- **URL según guía v4**: `https://servizos.meteogalicia.gal/apiv4/getNumericForecastInfo?coords=lon,lat&variables=wind,precipitation_amount,significative_wave_height&API_KEY=***`
- **Resultado**: HTTP **404 Not Found** (también la base `https://servizos.meteogalicia.gal/apiv4/`).
- **Conclusión**: El servicio apiv4 en ese dominio no está activo. La aplicación usa Open-Meteo como fallback cuando MeteoGalicia (apiv4) falla.

---

## Referencias

- Guía API MeteoSIX v4 (2021): [readkong.com – Guía API MeteoSIX v4 MeteoGalicia](https://es.readkong.com/page/gu-a-de-la-api-del-meteosix-versi-n-v4-meteogalicia-4760883)
- Cliente Python que usa los servicios mgrss: [Danieldiazi/meteogalicia-api](https://github.com/Danieldiazi/meteogalicia-api) (const.py con las URLs actuales).
- Documentación RSS/JSON MeteoGalicia: [meteogalicia.gal – RSS](https://www.meteogalicia.gal/web/RSS/rssIndex.action?request_locale=es)
- IDs de concellos: [JSON_Pred_Concello_es.pdf](https://www.meteogalicia.gal/datosred/infoweb/meteo/docs/rss/JSON_Pred_Concello_es.pdf)

---

## Posible ampliación del proyecto

Si se quiere usar **datos abiertos de MeteoGalicia** aunque no esté disponible la apiv4 numérica, se puede integrar la API de predicción por concello (mgrss) para, por ejemplo:

- Mostrar predicción oficial por días (temperatura, probabilidad de lluvia, tendencia de viento).
- Combinar con Open-Meteo para viento en km/h y oleaje hora a hora y seguir calculando el score de recomendación costa 1–10.

Eso requeriría un nuevo módulo (p. ej. `services/meteogalicia_mgrss.py`) y decidir cómo mezclar ambas fuentes en el score.
