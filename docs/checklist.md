# Чек-лист и публикация

## Результаты

| № | Результат | Проверка |
|---|-----------|----------|
| 1 | Compose поднимает API и БД | `docker compose up --build` |
| 2 | PostGIS и таблицы | `psql` → `\dt`, `postgis_version()` |
| 3 | Upload GPX | `POST /routes/upload` |
| 4 | XML/GPX валидация | `src/gpx.py` |
| 5 | Точки в БД | `track_points` |
| 6 | Дистанция и уклон | поля точки |
| 7 | Сегменты | `route_segments` |
| 8 | PNG карты | `output/maps/` |
| 9 | MapLibre | http://localhost:8000/ |
| 10 | Окружение 500 м | `POST /routes/{id}/environment` |
| 11 | Температура | `temperature_c` |
| 12 | Анализ | `POST /routes/{id}/analyze` |
| 13 | Кластеры | `cluster_id` |
| 14 | Batch ≥ 3 GPX | `python -m src.jobs` |
| 15 | Отчёт | `output/reports/import_report.json` |

## Минимальный набор файлов

```text
README.md .gitignore .env.example requirements.txt
Dockerfile compose.yml db/schema.sql
src/settings.py src/db.py src/main.py src/gpx.py src/jobs.py
web/index.html xsd/gpx-1.1.xsd
samples/   # пустая папка — положи ≥ 3 GPX сам
docs/*.md
```

## Что можно брать как основу

Разрешено: структура, Docker, `.env.example`, подключение к БД, заглушки, README/docs.

Нельзя: чужой готовый проект целиком, код без понимания, чужое ТЗ/отчёт.

## Публикация

```bash
git init -b main
git add .
git commit -m "feat: initial scaffold"
git remote add origin https://github.com/ТВОЙ_НИК/gpx-platform.git
git push -u origin main
```

Шаблон GitHub: Settings → Template repository → Use this template.

## Порядок работ

1. Compose + schema + health  
2. `src/gpx.py` по `docs/parser.md`  
3. Upload в Swagger  
4. `enrich_environment` / `render_map_image`  
5. MapLibre-линия  
6. `analyze_route`  
7. `run_batch_import`  
8. README и финальный чек  

## Перед сдачей

- [ ] `docker compose up --build`
- [ ] `/docs` и `/health`
- [ ] GPX загружается; битый XML отклоняется; дубликат блокируется
- [ ] Точки и сегменты в БД
- [ ] MapLibre без Leaflet; PNG сохранён
- [ ] Окружение 500 м; температура; анализ; кластеры
- [ ] Batch ≥ 3; отчёт импорта
- [ ] `.env` не в Git; README с источниками; история коммитов твоя
