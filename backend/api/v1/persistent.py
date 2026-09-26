"""
FIREGUARD AI - Persistent Sources API (Requirement 7)
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from backend.database.session import get_db
from backend.schemas.pydantic_models import PersistentSourceResponse
from backend.services.persistent_service import PersistentDetectorService

router = APIRouter(prefix="/persistent-sources", tags=["Persistent Thermal Sources"])

@router.get("", response_model=List[PersistentSourceResponse], summary="List monitored persistent industrial sources")
def list_persistent_sources(db: Session = Depends(get_db)):
    """
    Requirement 7:
    Returns historical hotspot clusters, frequency, average intensity, persistence score, and 2.5σ anomaly flags.
    """
    return PersistentDetectorService.get_all(db)

@router.get("/{id}", response_model=PersistentSourceResponse, summary="Get persistent source details by ID")
def get_persistent_source(
    id: str = Path(..., example="ps-jamnagar-flare"),
    db: Session = Depends(get_db)
):
    source = PersistentDetectorService.get_by_id(db, id)
    if not source:
        raise HTTPException(
            status_code=404,
            detail={"code": "SOURCE_NOT_FOUND", "message": f"Persistent source '{id}' not found"}
        )
    return source
