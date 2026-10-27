"""Small FastAPI adapter for the SafeNova custom frontend.

The sample records are illustrative only. Replace these with the existing
imagery/approval/GIS analysis services when those data sources are configured.
Saved areas are in-memory for this prototype; use a database for persistence.
"""
from datetime import datetime, timezone
from threading import Lock
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(title="SafeNova API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict to the deployed frontend origin in production.
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

DEMO_ALERTS = [
    {"id": "B-032", "lat": 12.9277, "lng": 80.1038, "priority": "High", "status": "Needs review", "note": "Illustrative demo record"},
    {"id": "B-017", "lat": 12.9294, "lng": 80.1071, "priority": "High", "status": "Needs review", "note": "Illustrative demo record"},
    {"id": "B-041", "lat": 12.9255, "lng": 80.0997, "priority": "Medium", "status": "Pending review", "note": "Illustrative demo record"},
    {"id": "B-008", "lat": 12.9310, "lng": 80.1011, "priority": "Low", "status": "Queued", "note": "Illustrative demo record"},
    {"id": "B-021", "lat": 12.9242, "lng": 80.1063, "priority": "Medium", "status": "Pending review", "note": "Illustrative demo record"},
    {"id": "B-015", "lat": 12.9288, "lng": 80.0969, "priority": "Low", "status": "Queued", "note": "Illustrative demo record"},
]
_saved_areas: list[dict[str, Any]] = []
_lock = Lock()


class AreaPayload(BaseModel):
    name: str = Field(default="Selected area", min_length=1, max_length=120)
    geometry: dict[str, Any]
    created_at: str | None = None


@app.get("/health")
def health():
    return {"status": "ok", "service": "safenova-api"}


@app.get("/api/alerts")
def get_alerts():
    return {"source": "demo", "alerts": DEMO_ALERTS, "note": "Illustrative records, not official findings."}


@app.get("/api/areas")
def get_areas():
    with _lock:
        return {"areas": list(_saved_areas)}


@app.post("/api/areas", status_code=201)
def save_area(area: AreaPayload):
    geometry = area.geometry
    if geometry.get("type") not in {"Feature", "Polygon", "Point", "MultiPolygon"}:
        raise HTTPException(status_code=422, detail="Unsupported GeoJSON geometry.")
    record = {
        "id": f"area-{len(_saved_areas) + 1}",
        "name": area.name.strip(),
        "geometry": geometry,
        "created_at": area.created_at or datetime.now(timezone.utc).isoformat(),
    }
    with _lock:
        _saved_areas.append(record)
    return {"saved": True, "area": record}
