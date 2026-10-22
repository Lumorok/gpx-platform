"""Фоновые и предметные задачи поверх импортированного маршрута.

См. docs/setup.md и docs/checklist.md.
"""

from typing import Any

from sqlalchemy.orm import Session

from src.settings import ENVIRONMENT_RADIUS_M, SAMPLES_DIR


def enrich_environment(route_id: int, db: Session) -> dict[str, Any]:
    """Overpass around:{radius},LAT,LON + Open-Meteo → temperature_c."""
    raise NotImplementedError(
        f"Окружение в радиусе {ENVIRONMENT_RADIUS_M} м — docs/setup.md"
    )


def render_map_image(route_id: int, db: Session) -> dict[str, Any]:
    """PNG карты → output/maps/route_{id}.png + таблица map_images."""
    raise NotImplementedError("Рендер PNG-карты — docs/setup.md")


def analyze_route(route_id: int, db: Session) -> dict[str, Any]:
    """Статистика, корреляции, кластеры → cluster_id, output/reports/."""
    raise NotImplementedError("Анализ и кластеризация — docs/setup.md")


def run_batch_import() -> dict[str, Any]:
    """Импорт ≥ 3 GPX из samples/ и отчёт output/reports/import_report.json."""
    files = sorted(SAMPLES_DIR.glob("*.gpx")) if SAMPLES_DIR.exists() else []
    print(f"Образцы GPX: {len(files)}")
    for path in files:
        print(f" - {path.name}")
    raise NotImplementedError("Пакетный импорт — docs/setup.md")


if __name__ == "__main__":
    run_batch_import()
