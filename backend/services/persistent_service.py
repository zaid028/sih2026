"""
FIREGUARD AI - PersistentDetectorService (Requirement 7)
Analyzes historical hotspot observations, clusters persistent sources, and identifies 2.5σ anomalies.
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from backend.models.entities import PersistentSource, ThermalHotspot, IndustrialFacility
from backend.ai.persistence import analyze_hotspot_persistence

class PersistentDetectorService:
    """Service tracking persistent thermal sources across industrial clusters."""

    @staticmethod
    def get_all(db: Session) -> List[Dict[str, Any]]:
        """Get all monitored persistent thermal sources."""
        sources = db.query(PersistentSource).all()
        return [s.to_dict() for s in sources]

    @staticmethod
    def get_by_id(db: Session, source_id: str) -> Optional[Dict[str, Any]]:
        """Get single persistent source by ID."""
        s = db.query(PersistentSource).filter(PersistentSource.id == source_id).first()
        if not s:
            return None
        data = s.to_dict()
        if s.facility:
            data["nearby_facility"] = s.facility.to_dict()
        return data

    @staticmethod
    def evaluate_persistence(db: Session, lat: float, lon: float, frp: float) -> Dict[str, Any]:
        """Runs temporal clustering and returns persistence metric."""
        all_hotspots = db.query(ThermalHotspot).all()
        hs_list = [{"latitude": h.latitude, "longitude": h.longitude, "frp": h.frp} for h in all_hotspots]
        return analyze_hotspot_persistence(frp, lat, lon, hs_list)
