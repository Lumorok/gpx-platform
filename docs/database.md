# База данных: PostgreSQL и PostGIS

## Цель

При первом создании тома `pgdata` PostgreSQL выполняет `db/schema.sql`:

1. включает расширение PostGIS;
2. создаёт таблицы маршрутов, точек, сегментов, логов и результатов;
3. добавляет индекс по `route_id` и GiST по `geom`.

PostGIS нужен для `geometry(Point, 4326)` и пространственных запросов (буфер 500 м).

## Файлы

```text
db/schema.sql
compose.yml          # volume → /docker-entrypoint-initdb.d/
src/db.py            # engine, Session, ORM-модели
src/settings.py      # DATABASE_URL
```

## Таблицы

| Таблица | Назначение |
|---------|------------|
| `routes` | маршрут, файл, SHA-256 |
| `track_points` | точки + geom, высота, уклон, температура |
| `map_images` | путь PNG и bbox |
| `environment_features` | объекты окружения у точки |
| `route_segments` | сегменты и `cluster_id` |
| `analysis_results` | JSON анализа |
| `import_logs` | статус импорта, уникальный `file_hash` |

Скрипт выполняется **только при первом** создании тома. После правок схемы:

```bash
docker compose down -v
docker compose up --build
```

## ORM

Модели в `src/db.py` зеркалят SQL. Геометрия:

```python
geom = Column(Geometry(geometry_type="POINT", srid=4326), nullable=False)
```

SRID `4326` — WGS84 (широта/долгота).

Зависимость: `geoalchemy2==0.15.2`.

## Проверка

```bash
docker compose exec db psql -U gpx_user -d gpx_db
```

```sql
\dt
SELECT postgis_version();
\q
```

## Источники

- [PostgreSQL](https://www.postgresql.org/docs/)
- [PostGIS](https://postgis.net/documentation/)
- [FastAPI + SQL](https://fastapi.tiangolo.com/tutorial/sql-databases/)
- [SQLAlchemy](https://docs.sqlalchemy.org/)
- [GeoAlchemy2](https://geoalchemy-2.readthedocs.io/)
