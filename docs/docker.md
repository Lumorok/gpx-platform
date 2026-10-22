# Docker: API и PostGIS

## Цель

Два сервиса в одной внутренней сети Compose:

1. **api** — FastAPI на порту `8000` (публикуется наружу).
2. **db** — PostgreSQL + PostGIS (только `expose: 5432`, без `ports`).

Так база недоступна из интернета, а контейнеры видят друг друга по имени сервиса (`db`).

## Установка

- Windows/macOS: [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- Linux: [Engine](https://docs.docker.com/engine/install/)

```bash
docker --version
docker compose version
```

## Файлы этого этапа

```text
compose.yml
Dockerfile
.env.example
requirements.txt
src/settings.py
src/db.py
src/main.py
web/index.html
```

## Переменные окружения

`.env.example`:

```env
POSTGRES_USER=gpx_user
POSTGRES_PASSWORD=change_me_strong_password
POSTGRES_DB=gpx_db
DATABASE_URL=postgresql+psycopg2://gpx_user:change_me_strong_password@db:5432/gpx_db
```

```bash
cp .env.example .env
```

Пароль в `POSTGRES_PASSWORD` и в `DATABASE_URL` должен совпадать. Файл `.env` не коммитится.

## Compose

Ключевые правила:

| Сервис | Порты | Зависимости |
|--------|-------|-------------|
| `db` | только `expose: 5432` | volume `pgdata` + `db/schema.sql` |
| `api` | `8000:8000` | `depends_on` + `service_healthy` |

Запуск:

```bash
docker compose up --build
```

Проверка: http://localhost:8000/docs и http://localhost:8000/health

Остановка:

```bash
docker compose down
docker compose down -v   # с очисткой тома БД
```

## Что уже в репозитории

`Dockerfile`, `compose.yml`, `src/settings.py`, `src/db.py`, `src/main.py` с `GET /health` — готовый каркас. Дальше подключай парсер и задачи.

## Источники

- [Compose](https://docs.docker.com/compose/)
- [Модель приложения](https://docs.docker.com/compose/intro/compose-application-model/)
- [Getting started](https://docs.docker.com/compose/gettingstarted/)
