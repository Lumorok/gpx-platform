"""Точка входа FastAPI: health + каркас маршрутов REST."""

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from src.db import Route, TrackPoint, get_db
from src.gpx import import_gpx
from src.jobs import analyze_route, enrich_environment, render_map_image

app = FastAPI(title="GPX Route Analytics Platform")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/routes/upload")
async def upload_route(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename or not file.filename.lower().endswith(".gpx"):
        raise HTTPException(status_code=400, detail="Ожидается файл .gpx")
    try:
        return import_gpx(file, db)
    except NotImplementedError as exc:
        raise HTTPException(status_code=501, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/routes")
def list_routes(db: Session = Depends(get_db)):
    return db.query(Route).order_by(Route.id.desc()).all()


@app.get("/routes/{route_id}/points")
def route_points(route_id: int, db: Session = Depends(get_db)):
    route = db.query(Route).filter(Route.id == route_id).first()
    if not route:
        raise HTTPException(status_code=404, detail="Маршрут не найден")
    return (
        db.query(TrackPoint)
        .filter(TrackPoint.route_id == route_id)
        .order_by(TrackPoint.point_order)
        .all()
    )


@app.post("/routes/{route_id}/environment")
def route_environment(route_id: int, db: Session = Depends(get_db)):
    try:
        return enrich_environment(route_id, db)
    except NotImplementedError as exc:
        raise HTTPException(status_code=501, detail=str(exc)) from exc


@app.post("/routes/{route_id}/map-image")
def route_map_image(route_id: int, db: Session = Depends(get_db)):
    try:
        return render_map_image(route_id, db)
    except NotImplementedError as exc:
        raise HTTPException(status_code=501, detail=str(exc)) from exc


@app.post("/routes/{route_id}/analyze")
def route_analyze(route_id: int, db: Session = Depends(get_db)):
    try:
        return analyze_route(route_id, db)
    except NotImplementedError as exc:
        raise HTTPException(status_code=501, detail=str(exc)) from exc


app.mount("/", StaticFiles(directory="web", html=True), name="web")
