"""
FIREGUARD AI - FastAPI Main Application Server
SIH Problem Statement SIH26162:
“AI-Based Detection and Classification of Industrial Fires and Persistent Thermal Sources Using NASA FIRMS, OSM & Satellite Data”
"""
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse, FileResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from backend.config.settings import settings, WORKSPACE_DIR
from backend.database.session import engine, Base, SessionLocal
from backend.database.seed import seed_database_if_empty
from backend.api import v1_router, legacy_router

FRONTEND_DIR = WORKSPACE_DIR / "frontend"

import asyncio
from backend.services.firms_service import FIRMSService
from backend.api.v1.websocket import broadcast_realtime_event

async def periodic_firms_ingestion():
    """Requirement 3: Background processing for periodic ingestion."""
    while True:
        try:
            await asyncio.sleep(120)  # Ingest every 2 minutes
            db = SessionLocal()
            try:
                def broadcast_cb(payload):
                    broadcast_realtime_event("HOTSPOT_INGESTED", payload)
                FIRMSService.ingest_observations(db, broadcast_fn=broadcast_cb)
            finally:
                db.close()
        except asyncio.CancelledError:
            break
        except Exception:
            pass

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure tables created and database seeded
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_database_if_empty(db)
    finally:
        db.close()

    # Start periodic background ingestion task
    bg_task = asyncio.create_task(periodic_firms_ingestion())
    yield
    # Shutdown logic
    bg_task.cancel()

app = FastAPI(
    title="FIREGUARD AI - Mission Command & Geospatial Analytics API",
    description="""
## FIREGUARD AI Tactical Command & Satellite Observation Platform
**Smart India Hackathon Problem Statement SIH26162**

Intelligent real-time monitoring combining:
- **NASA FIRMS** (MODIS & VIIRS SNPP / NOAA-20 NRT) Thermal Anomaly Feeds
- **OpenStreetMap / Overpass** Spatial Facility & Emergency Infrastructure Buffering
- **Spatiotemporal Recurrence Engine** with 2.5σ Anomaly Spike Detection
- **8-Class AI Fire Classifier** with Explainable AI (XAI) Factor Attribution
- **Multi-Factor ISO31000 Risk Scorer** (0-100 Explainable Scale)
- **Dynamic Safe Routing Engine** with Hazard Buffer Zone Bypass
- **Multi-Agency Tactical Alert Dispatcher** (SMS, Email, Push)
- **Real-Time WebSockets** for live dashboard telemetry
    """,
    version=settings.VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Standard Error Handling (Requirement 22)
@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    code = "HTTP_ERROR"
    message = str(exc.detail)
    if isinstance(exc.detail, dict):
        code = exc.detail.get("code", "ERROR")
        message = exc.detail.get("message", str(exc.detail))
    elif exc.status_code == 404:
        code = "RESOURCE_NOT_FOUND"
    elif exc.status_code == 401:
        code = "UNAUTHORIZED"
    elif exc.status_code == 403:
        code = "FORBIDDEN"

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": code,
                "message": message
            }
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    first_msg = errors[0].get("msg") if errors else "Validation failed"
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": f"Invalid request parameters: {first_msg}",
                "details": {"validation_errors": errors}
            }
        }
    )

# Include Routers
app.include_router(v1_router)
app.include_router(legacy_router)

# Frontend Static Files & Routes
if FRONTEND_DIR.exists():
    # Mount subdirectories
    for subdir in ["css", "js", "assets"]:
        p = FRONTEND_DIR / subdir
        if p.exists():
            app.mount(f"/{subdir}", StaticFiles(directory=str(p)), name=subdir)

    @app.get("/", include_in_schema=False)
    async def serve_landing_page():
        landing_file = FRONTEND_DIR / "index.html"
        if landing_file.exists():
            return FileResponse(str(landing_file))
        return JSONResponse({"status": "FIREGUARD AI API Online", "docs": "/docs"})

    @app.get("/login", include_in_schema=False)
    async def serve_login_page():
        login_file = FRONTEND_DIR / "login.html"
        if login_file.exists():
            return FileResponse(str(login_file))
        return RedirectResponse(url="/app")

    @app.get("/logout", include_in_schema=False)
    async def handle_logout():
        return RedirectResponse(url="/login")

    @app.get("/app", include_in_schema=False)
    async def serve_command_center():
        app_file = FRONTEND_DIR / "app.html"
        if app_file.exists():
            return FileResponse(str(app_file))
        return JSONResponse({"status": "Command Center View"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
