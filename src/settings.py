"""Конфигурация окружения и путей проекта."""

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://gpx_user:gpx_password@localhost:5432/gpx_db",
)

XSD_FILE = ROOT / "xsd" / "gpx-1.1.xsd"
SAMPLES_DIR = ROOT / "samples"
OUTPUT_DIR = ROOT / "output"
MAPS_DIR = OUTPUT_DIR / "maps"
REPORTS_DIR = OUTPUT_DIR / "reports"

ENVIRONMENT_RADIUS_M = 500
OVERPASS_URL = "https://overpass-api.de/api/interpreter"
OPEN_METEO_URL = "https://archive-api.open-meteo.com/v1/archive"
