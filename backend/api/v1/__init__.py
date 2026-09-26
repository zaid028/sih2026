from fastapi import APIRouter
from .hotspots import router as hotspots_router
from .facilities import router as facilities_router
from .emergency import router as emergency_router
from .roads import router as roads_router
from .analyze import router as analyze_router
from .ai import router as ai_router
from .persistent import router as persistent_router
from .risk import router as risk_router
from .incidents import router as incidents_router
from .routes import router as routes_router
from .emergency_contacts import router as emergency_contacts_router
from .alerts import router as alerts_router
from .websocket import router as ws_router
from .analytics import router as analytics_router
from .auth import router as auth_router
from .demo import router as demo_router
from .health import router as health_router

v1_router = APIRouter(prefix="/api/v1")

v1_router.include_router(hotspots_router)
v1_router.include_router(facilities_router)
v1_router.include_router(emergency_router)
v1_router.include_router(roads_router)
v1_router.include_router(analyze_router)
v1_router.include_router(ai_router)
v1_router.include_router(persistent_router)
v1_router.include_router(risk_router)
v1_router.include_router(incidents_router)
v1_router.include_router(routes_router)
v1_router.include_router(emergency_contacts_router)
v1_router.include_router(alerts_router)
v1_router.include_router(ws_router)
v1_router.include_router(analytics_router)
v1_router.include_router(auth_router)
v1_router.include_router(demo_router)
v1_router.include_router(health_router)

__all__ = ["v1_router"]
