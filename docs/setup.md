# Сборка системы

## Конвейер

```text
GPX → src/gpx.py → PostGIS → src/main.py → MapLibre → src/jobs.py
```

## Структура проекта

```text
gpx-platform/
├── README.md
├── .gitignore
├── .env.example
├── requirements.txt
├── Dockerfile
├── compose.yml
├── db/schema.sql
├── src/
│   ├── settings.py
│   ├── db.py
│   ├── main.py
│   ├── gpx.py
│   └── jobs.py
├── web/index.html
├── xsd/gpx-1.1.xsd
├── samples/
└── docs/
```

## Зависимости

Базовые уже в `requirements.txt`. При необходимости карты на тайлах можно добавить `contextily` / `geopandas` / `rasterio` — они тяжелее для slim-образа; для PNG достаточно matplotlib + shapely/pyproj.

## Запуск

```bash
cp .env.example .env
docker compose up --build
```

## API

```bash
# импорт
curl -X POST "http://localhost:8000/routes/upload" -F "file=@samples/track_a.gpx"

# окружение 500 м (Overpass around:500,LAT,LON) + температура Open-Meteo
curl -X POST "http://localhost:8000/routes/1/environment"

# PNG → output/maps/route_1.png
curl -X POST "http://localhost:8000/routes/1/map-image"

# статистика, корреляции, cluster_id
curl -X POST "http://localhost:8000/routes/1/analyze"
```

Карта: http://localhost:8000/ — MapLibre, без Leaflet.

Пакетный импорт:

```bash
python -m src.jobs
```

Ожидание: ≥ 3 GPX и `output/reports/import_report.json`.

## Что реализовать

| Место | Задача |
|-------|--------|
| `src/gpx.py` | парсер + импорт (код в `docs/parser.md`) |
| `src/jobs.py` → `enrich_environment` | Overpass 500 м + Open-Meteo |
| `src/jobs.py` → `render_map_image` | PNG карты |
| `src/jobs.py` → `analyze_route` | pandas / sklearn, `cluster_id` |
| `src/jobs.py` → `run_batch_import` | batch + отчёт |
| `web/index.html` | линия трека из `GET /routes/{id}/points` |

Маршруты в `src/main.py` уже разведены: после реализации функций endpoint'ы заработают без смены URL.

## Источники

- [Overpass QL](https://wiki.openstreetmap.org/wiki/Overpass_API/Overpass_QL)
- [Open-Meteo](https://open-meteo.com/en/docs/historical-weather-api)
- [MapLibre](https://maplibre.org/maplibre-gl-js/docs/)
- [scikit-learn](https://scikit-learn.org/stable/)
