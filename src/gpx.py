"""Собственный GPX/XML-парсер и импорт в БД.

Реализация — по docs/parser.md:
1) безопасный разбор XML (lxml, без XXE);
2) проверка namespace GPX 1.1 и версии;
3) валидация по xsd/gpx-1.1.xsd;
4) извлечение metadata / wpt / trk → trkseg → trkpt;
5) SHA-256, защита от дубликатов, Haversine, уклон, запись в PostGIS.
"""

from typing import Any

from sqlalchemy.orm import Session

GPX_NS = "http://www.topografix.com/GPX/1/1"


class GpxError(ValueError):
    """Некорректный GPX/XML."""


def parse_gpx(upload_file) -> dict[str, Any]:
    """Вернуть dict: metadata, waypoints, tracks, xsd_errors."""
    raise NotImplementedError("Реализуй парсер — docs/parser.md")


def import_gpx(upload_file, db: Session) -> dict[str, Any]:
    """Сохранить маршрут и точки. Вернуть route_id и счётчики."""
    raise NotImplementedError("Реализуй импорт — docs/parser.md")
