CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE routes (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    source_file TEXT NOT NULL,
    file_hash TEXT UNIQUE NOT NULL,
    region TEXT,
    date_start TIMESTAMP,
    date_end TIMESTAMP,
    uploaded_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE track_points (
    id SERIAL PRIMARY KEY,
    route_id INTEGER NOT NULL REFERENCES routes(id) ON DELETE CASCADE,
    point_order INTEGER NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    geom geometry(Point, 4326) NOT NULL,
    elevation_m DOUBLE PRECISION,
    recorded_at TIMESTAMP,
    temperature_c DOUBLE PRECISION,
    step_frequency DOUBLE PRECISION,
    terrain_type TEXT,
    surrounding_objects JSONB NOT NULL DEFAULT '{}'::jsonb,
    distance_from_prev_m DOUBLE PRECISION NOT NULL DEFAULT 0,
    slope_percent DOUBLE PRECISION
);

CREATE INDEX idx_track_points_route ON track_points(route_id);
CREATE INDEX idx_track_points_geom ON track_points USING GIST(geom);

CREATE TABLE map_images (
    id SERIAL PRIMARY KEY,
    route_id INTEGER NOT NULL REFERENCES routes(id) ON DELETE CASCADE,
    image_path TEXT NOT NULL,
    bbox JSONB NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE environment_features (
    id SERIAL PRIMARY KEY,
    track_point_id INTEGER NOT NULL REFERENCES track_points(id) ON DELETE CASCADE,
    feature_type TEXT NOT NULL,
    feature_name TEXT,
    distance_m DOUBLE PRECISION,
    properties JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE route_segments (
    id SERIAL PRIMARY KEY,
    route_id INTEGER NOT NULL REFERENCES routes(id) ON DELETE CASCADE,
    segment_order INTEGER NOT NULL,
    start_point_id INTEGER REFERENCES track_points(id),
    end_point_id INTEGER REFERENCES track_points(id),
    length_m DOUBLE PRECISION NOT NULL,
    elevation_gain_m DOUBLE PRECISION NOT NULL DEFAULT 0,
    elevation_loss_m DOUBLE PRECISION NOT NULL DEFAULT 0,
    avg_slope_percent DOUBLE PRECISION,
    max_slope_percent DOUBLE PRECISION,
    terrain_type TEXT,
    difficulty_score DOUBLE PRECISION,
    cluster_id INTEGER
);

CREATE TABLE analysis_results (
    id SERIAL PRIMARY KEY,
    route_id INTEGER REFERENCES routes(id) ON DELETE CASCADE,
    analysis_type TEXT NOT NULL,
    result_json JSONB NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE import_logs (
    id SERIAL PRIMARY KEY,
    file_name TEXT NOT NULL,
    file_hash TEXT UNIQUE NOT NULL,
    status TEXT NOT NULL,
    message TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
