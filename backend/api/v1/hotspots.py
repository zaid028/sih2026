"""
FIREGUARD AI - Hotspots API (Requirement 2 & 3)
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from backend.database.session import get_db
from backend.models.entities import ThermalHotspot
from backend.schemas.pydantic_models import HotspotResponse, HotspotIngestResponse
from backend.services.firms_service import FIRMSService
from backend.utils.geo import haversine_distance_km

router = APIRouter(prefix="/hotspots", tags=["Hotspots (NASA FIRMS)"])

@router.get("", response_model=List[HotspotResponse], summary="Fetch thermal hotspots with filtering")
def get_hotspots(
    latitude: Optional[float] = Query(None, description="Center latitude for radial search", example=22.4707),
    longitude: Optional[float] = Query(None, description="Center longitude for radial search", example=70.0577),
    radius: Optional[float] = Query(None, description="Search radius in kilometers", example=50.0),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)", example="2026-09-01"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)", example="2026-09-30"),
    confidence: Optional[float] = Query(None, description="Minimum confidence score (0-100)", example=75.0),
    source: Optional[str] = Query(None, description="Filter by detection source", example="NASA FIRMS"),
    risk_level: Optional[str] = Query(None, description="Filter by risk level (CRITICAL, HIGH, MODERATE, LOW)", example="CRITICAL"),
    classification: Optional[str] = Query(None, description="Filter by AI class", example="Industrial Fire"),
    db: Session = Depends(get_db)
):
    """
    Returns satellite thermal anomalies with AI classification and explainable risk scores.
    """
    query = db.query(ThermalHotspot)

    if confidence is not None:
        query = query.filter(ThermalHotspot.confidence >= confidence)
    if risk_level:
        query = query.filter(ThermalHotspot.risk_level == risk_level.upper())
    if classification:
        query = query.filter(ThermalHotspot.classification == classification)
    if source:
        query = query.filter(ThermalHotspot.source.ilike(f"%{source}%"))
    if start_date:
        query = query.filter(ThermalHotspot.acq_date >= start_date)
    if end_date:
        query = query.filter(ThermalHotspot.acq_date <= end_date)

    hotspots = query.order_by(ThermalHotspot.created_at.desc()).all()

    # Spatial radial filtering if lat/lon/radius provided
    if latitude is not None and longitude is not None and radius is not None:
        filtered = []
        for h in hotspots:
            dist = haversine_distance_km(latitude, longitude, h.latitude, h.longitude)
            if dist <= radius:
                filtered.append(h)
        hotspots = filtered

    return [h.to_dict() for h in hotspots]


@router.post("/ingest", response_model=HotspotIngestResponse, summary="Ingest thermal observations from NASA FIRMS")
def ingest_hotspots(
    country: str = Query("IND", description="ISO-3 Country Code", example="IND"),
    day_range: int = Query(1, description="Past days range (1-10)", ge=1, le=10),
    db: Session = Depends(get_db)
):
    """
    Requirement 3 & 10:
    Trigger end-to-end ingestion from NASA FIRMS VIIRS/MODIS feed:
    1. Fetch observations
    2. Validate and normalize records
    3. Geospatial processing & correlate with nearest industrial facility
    4. Run 8-Class AI classification with XAI factors
    5. Calculate ISO31000 explainable risk score
    6. Auto-create incident & alert if risk threshold exceeded
    7. Broadcast live update to WebSockets
    """
    from backend.api.v1.websocket import broadcast_realtime_event

    def broadcast_callback(payload):
        broadcast_realtime_event("HOTSPOT_INGESTED", payload)

    try:
        records = FIRMSService.fetch_and_normalize(country=country, day_range=day_range)
        result = FIRMSService.ingest_observations(db, records=records, broadcast_fn=broadcast_callback)
        inc_msg = f", {result.get('incidents_created', 0)} incidents auto-triaged" if result.get('incidents_created') else ""
        return HotspotIngestResponse(
            success=True,
            ingested_count=result["ingested_count"],
            source=result["source"],
            message=f"Ingestion successful: {result['ingested_count']} new, {result['updated_count']} updated{inc_msg}."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail={"code": "INGEST_FAILED", "message": str(e)})
