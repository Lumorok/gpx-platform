"""Подключение к PostgreSQL/PostGIS и ORM-модели.

Схема таблиц создаётся из db/schema.sql при первом старте контейнера БД.
"""

from datetime import datetime

from geoalchemy2 import Geometry
from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import declarative_base, sessionmaker

from src.settings import DATABASE_URL

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class Route(Base):
    __tablename__ = "routes"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    source_file = Column(String, nullable=False)
    file_hash = Column(String, nullable=False, unique=True)
    region = Column(String)
    date_start = Column(DateTime)
    date_end = Column(DateTime)
    uploaded_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class TrackPoint(Base):
    __tablename__ = "track_points"

    id = Column(Integer, primary_key=True)
    route_id = Column(Integer, ForeignKey("routes.id", ondelete="CASCADE"), nullable=False)
    point_order = Column(Integer, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    geom = Column(Geometry(geometry_type="POINT", srid=4326), nullable=False)
    elevation_m = Column(Float)
    recorded_at = Column(DateTime)
    temperature_c = Column(Float)
    step_frequency = Column(Float)
    terrain_type = Column(String)
    surrounding_objects = Column(JSONB, nullable=False, default=dict)
    distance_from_prev_m = Column(Float, nullable=False, default=0.0)
    slope_percent = Column(Float)


class MapImage(Base):
    __tablename__ = "map_images"

    id = Column(Integer, primary_key=True)
    route_id = Column(Integer, ForeignKey("routes.id", ondelete="CASCADE"), nullable=False)
    image_path = Column(String, nullable=False)
    bbox = Column(JSONB, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class EnvironmentFeature(Base):
    __tablename__ = "environment_features"

    id = Column(Integer, primary_key=True)
    track_point_id = Column(
        Integer, ForeignKey("track_points.id", ondelete="CASCADE"), nullable=False
    )
    feature_type = Column(String, nullable=False)
    feature_name = Column(String)
    distance_m = Column(Float)
    properties = Column(JSONB, nullable=False, default=dict)


class RouteSegment(Base):
    __tablename__ = "route_segments"

    id = Column(Integer, primary_key=True)
    route_id = Column(Integer, ForeignKey("routes.id", ondelete="CASCADE"), nullable=False)
    segment_order = Column(Integer, nullable=False)
    start_point_id = Column(Integer, ForeignKey("track_points.id"))
    end_point_id = Column(Integer, ForeignKey("track_points.id"))
    length_m = Column(Float, nullable=False)
    elevation_gain_m = Column(Float, nullable=False, default=0.0)
    elevation_loss_m = Column(Float, nullable=False, default=0.0)
    avg_slope_percent = Column(Float)
    max_slope_percent = Column(Float)
    terrain_type = Column(String)
    difficulty_score = Column(Float)
    cluster_id = Column(Integer)


class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True)
    route_id = Column(Integer, ForeignKey("routes.id", ondelete="CASCADE"))
    analysis_type = Column(String, nullable=False)
    result_json = Column(JSONB, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class ImportLog(Base):
    __tablename__ = "import_logs"

    id = Column(Integer, primary_key=True)
    file_name = Column(String, nullable=False)
    file_hash = Column(String, nullable=False, unique=True)
    status = Column(String, nullable=False)
    message = Column(Text)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
