# Собственный парсер GPX/XML

## Цель

Реализовать в `src/gpx.py`:

1. корректный XML;
2. корневой `<gpx>` и namespace GPX 1.1;
3. версия `1.0` / `1.1`;
4. валидация по `xsd/gpx-1.1.xsd`;
5. metadata, треки, сегменты, точки, extensions;
6. импорт в PostGIS с Haversine и уклоном;
7. отказ дубликатов по SHA-256 (`import_logs`).

Namespace: `http://www.topografix.com/GPX/1/1`

## Файлы

```text
src/gpx.py
xsd/gpx-1.1.xsd
samples/track_a.gpx
```

Официальная XSD: https://www.topografix.com/GPX/1/1/gpx.xsd  
В репозитории уже лежит `xsd/gpx-1.1.xsd`.

## Безопасный разбор

```python
etree.XMLParser(
    resolve_entities=False,
    no_network=True,
    load_dtd=False,
    dtd_validation=False,
    huge_tree=False,
)
```

## Каркас функций (`src/gpx.py`)

```python
from datetime import datetime
from typing import Any
import hashlib
import math

from lxml import etree
from geoalchemy2.elements import WKTElement
from sqlalchemy.orm import Session

from src.settings import XSD_FILE
from src.db import ImportLog, Route, RouteSegment, TrackPoint

GPX_NS = "http://www.topografix.com/GPX/1/1"


class GpxError(ValueError):
    pass


def _safe_parser() -> etree.XMLParser:
    return etree.XMLParser(
        resolve_entities=False,
        no_network=True,
        load_dtd=False,
        dtd_validation=False,
        huge_tree=False,
    )


def parse_gpx(upload_file) -> dict[str, Any]:
    """XML → metadata, waypoints, tracks, xsd_errors."""
    try:
        tree = etree.parse(upload_file.file, _safe_parser())
    except etree.XMLSyntaxError as exc:
        raise GpxError(f"Invalid XML: {exc}") from exc

    root = tree.getroot()
    if root.tag != f"{{{GPX_NS}}}gpx":
        raise GpxError("Root must be <gpx> in GPX 1.1 namespace")

    version = root.get("version")
    if version not in {"1.0", "1.1"}:
        raise GpxError(f"Unsupported GPX version: {version}")

    xsd_errors = []
    if XSD_FILE.exists():
        schema = etree.XMLSchema(etree.parse(str(XSD_FILE)))
        if not schema.validate(tree):
            xsd_errors = [str(e) for e in schema.error_log]

    metadata_el = root.find(f"{{{GPX_NS}}}metadata")
    metadata = {}
    if metadata_el is not None:
        time_value = metadata_el.findtext(f"{{{GPX_NS}}}time")
        metadata = {
            "name": metadata_el.findtext(f"{{{GPX_NS}}}name"),
            "description": metadata_el.findtext(f"{{{GPX_NS}}}desc"),
            "time": (
                datetime.fromisoformat(time_value.replace("Z", "+00:00"))
                if time_value else None
            ),
        }

    waypoints = []
    for wpt in root.findall(f"{{{GPX_NS}}}wpt"):
        lat, lon = wpt.get("lat"), wpt.get("lon")
        if lat is None or lon is None:
            continue
        waypoints.append({
            "latitude": float(lat),
            "longitude": float(lon),
            "name": wpt.findtext(f"{{{GPX_NS}}}name"),
        })

    tracks = []
    for track_order, trk in enumerate(root.findall(f"{{{GPX_NS}}}trk")):
        segments = []
        for segment_order, seg in enumerate(trk.findall(f"{{{GPX_NS}}}trkseg")):
            points = []
            for pt in seg.findall(f"{{{GPX_NS}}}trkpt"):
                lat, lon = pt.get("lat"), pt.get("lon")
                if lat is None or lon is None:
                    continue
                latitude, longitude = float(lat), float(lon)
                if not -90 <= latitude <= 90:
                    raise GpxError(f"Invalid latitude: {latitude}")
                if not -180 <= longitude <= 180:
                    raise GpxError(f"Invalid longitude: {longitude}")
                elev = pt.findtext(f"{{{GPX_NS}}}ele")
                time_value = pt.findtext(f"{{{GPX_NS}}}time")
                extensions = pt.find(f"{{{GPX_NS}}}extensions")
                parsed_ext = {}
                if extensions is not None:
                    for el in extensions.iter():
                        if isinstance(el.tag, str):
                            parsed_ext[el.tag] = el.text
                points.append({
                    "latitude": latitude,
                    "longitude": longitude,
                    "elevation": float(elev) if elev else None,
                    "time": (
                        datetime.fromisoformat(time_value.replace("Z", "+00:00"))
                        if time_value else None
                    ),
                    "extensions": parsed_ext,
                })
            segments.append({"segment_order": segment_order, "points": points})
        tracks.append({
            "track_order": track_order,
            "name": trk.findtext(f"{{{GPX_NS}}}name"),
            "segments": segments,
        })

    if not tracks:
        raise GpxError("GPX file contains no tracks")

    return {
        "metadata": metadata,
        "waypoints": waypoints,
        "tracks": tracks,
        "xsd_errors": xsd_errors,
    }


def file_hash(upload_file) -> str:
    upload_file.file.seek(0)
    digest = hashlib.sha256(upload_file.file.read()).hexdigest()
    upload_file.file.seek(0)
    return digest


def haversine(lat1, lon1, lat2, lon2) -> float:
    r = 6371000.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def import_gpx(upload_file, db: Session) -> dict[str, Any]:
    digest = file_hash(upload_file)
    if db.query(ImportLog).filter(ImportLog.file_hash == digest).first():
        raise ValueError("GPX file already imported")

    try:
        parsed = parse_gpx(upload_file)
    except GpxError as exc:
        db.add(ImportLog(
            file_name=upload_file.filename,
            file_hash=digest,
            status="failed",
            message=str(exc),
        ))
        db.commit()
        raise ValueError(str(exc)) from exc

    meta = parsed["metadata"]
    route = Route(
        name=meta.get("name") or upload_file.filename,
        source_file=upload_file.filename,
        file_hash=digest,
        date_start=meta.get("time"),
        date_end=meta.get("time"),
    )
    db.add(route)
    db.flush()

    points_count = 0
    previous = None
    for track in parsed["tracks"]:
        for segment in track["segments"]:
            start_id = end_id = None
            length = gain = loss = 0.0
            slopes = []
            for point in segment["points"]:
                distance = 0.0
                slope = None
                if previous:
                    distance = haversine(
                        previous["latitude"], previous["longitude"],
                        point["latitude"], point["longitude"],
                    )
                    if (
                        point["elevation"] is not None
                        and previous["elevation"] is not None
                        and distance > 0
                    ):
                        diff = point["elevation"] - previous["elevation"]
                        slope = diff / distance * 100
                        slopes.append(slope)
                        if diff > 0:
                            gain += diff
                        else:
                            loss += abs(diff)

                row = TrackPoint(
                    route_id=route.id,
                    point_order=points_count,
                    latitude=point["latitude"],
                    longitude=point["longitude"],
                    geom=WKTElement(
                        f"POINT({point['longitude']} {point['latitude']})",
                        srid=4326,
                    ),
                    elevation_m=point["elevation"],
                    recorded_at=point["time"],
                    distance_from_prev_m=distance,
                    slope_percent=slope,
                    surrounding_objects=point["extensions"],
                )
                db.add(row)
                db.flush()
                if start_id is None:
                    start_id = row.id
                end_id = row.id
                length += distance
                previous = point
                points_count += 1

            if start_id and end_id:
                db.add(RouteSegment(
                    route_id=route.id,
                    segment_order=points_count,
                    start_point_id=start_id,
                    end_point_id=end_id,
                    length_m=length,
                    elevation_gain_m=gain,
                    elevation_loss_m=loss,
                    avg_slope_percent=(sum(slopes) / len(slopes) if slopes else None),
                    max_slope_percent=(max(slopes) if slopes else None),
                ))

    if points_count == 0:
        db.rollback()
        raise ValueError("No valid track points")

    db.add(ImportLog(
        file_name=upload_file.filename,
        file_hash=digest,
        status="success",
        message=f"Imported {points_count} points",
    ))
    db.commit()

    return {
        "route_id": route.id,
        "name": route.name,
        "points_count": points_count,
        "segments_count": len(parsed["tracks"]),
        "waypoints_count": len(parsed["waypoints"]),
        "xsd_errors": parsed["xsd_errors"],
    }
```

Перенеси реализацию в `src/gpx.py`, затем проверь:

```bash
curl -X POST "http://localhost:8000/routes/upload" \
  -F "file=@samples/track_a.gpx"
```

## Источники

- [GPX XSD](https://www.topografix.com/GPX/1/1/gpx.xsd)
- [lxml validation](https://lxml.de/validation.html)
