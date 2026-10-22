# GPX Route Analytics

Компактный каркас: Docker + PostGIS + FastAPI. Предметную логику пишешь сам по `docs/`.

```text
GPX → парсер → PostgreSQL/PostGIS → REST → MapLibre → анализ
```

## Структура

```text
compose.yml          # API + PostGIS (порт БД не наружу)
Dockerfile
db/schema.sql        # PostGIS и таблицы
src/
  settings.py        # env и пути
  db.py              # SQLAlchemy + модели
  main.py            # FastAPI и маршруты
  gpx.py             # парсер и импорт (заглушка)
  jobs.py            # окружение, карта, анализ, batch
web/index.html       # MapLibre UI
xsd/gpx-1.1.xsd
samples/             # сюда положи свои GPX (≥ 3 для агента)
docs/                # пошаговые инструкции
```

## Документация

| Файл | Тема |
|------|------|
| [docs/docker.md](docs/docker.md) | контейнеры и сеть |
| [docs/database.md](docs/database.md) | PostGIS и модели |
| [docs/parser.md](docs/parser.md) | GPX/XML и импорт |
| [docs/setup.md](docs/setup.md) | API, карта, анализ |
| [docs/checklist.md](docs/checklist.md) | сдача и публикация |

## Запуск

```bash
cp .env.example .env
docker compose up --build
```

- http://localhost:8000/docs
- http://localhost:8000/health
- http://localhost:8000/

`GET /health` и чтение маршрутов из БД уже работают. Парсер, обогащение, PNG, анализ и batch — реализуй по docs (пока `501`).

## Происхождение кода

Проект создан на основе собственного шаблона инфраструктуры.

- FastAPI — https://fastapi.tiangolo.com/
- PostgreSQL / PostGIS — https://www.postgresql.org/ / https://postgis.net/
- SQLAlchemy / GeoAlchemy2 — https://www.sqlalchemy.org/ / https://geoalchemy-2.readthedocs.io/
- lxml — https://lxml.de/
- MapLibre GL JS — https://maplibre.org/
- Overpass API — https://wiki.openstreetmap.org/wiki/Overpass_API
- Open-Meteo — https://open-meteo.com/
- scikit-learn — https://scikit-learn.org/

Предметная реализация выполняется в рамках данного проекта.
