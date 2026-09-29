"""
FIREGUARD AI - Database Connection & Session Management
Supports both PostgreSQL + PostGIS and SQLite with in-process spatial extensions.
"""
import math
from pathlib import Path
from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from backend.config.settings import settings

import os

db_url = settings.DATABASE_URL
if os.environ.get("VERCEL"):
    # Vercel serverless environment: only /tmp is writable
    db_file = Path("/tmp/fireguard.db")
    engine = create_engine(f"sqlite:///{db_file}", connect_args={"check_same_thread": False})
elif db_url.startswith("sqlite"):
    # Ensure data directory exists
    db_path_part = db_url.replace("sqlite:///", "")
    db_file = Path(db_path_part)
    if not db_file.is_absolute():
        from backend.config.settings import WORKSPACE_DIR
        db_file = WORKSPACE_DIR / db_path_part
    try:
        db_file.parent.mkdir(parents=True, exist_ok=True)
    except Exception:
        db_file = Path("/tmp/fireguard.db")
    engine = create_engine(f"sqlite:///{db_file}", connect_args={"check_same_thread": False})
else:
    engine = create_engine(db_url, pool_pre_ping=True)

# Register custom SQLite Haversine distance function if using SQLite
if db_url.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def register_spatial_sqlite_functions(dbapi_connection, connection_record):
        def haversine_km(lat1, lon1, lat2, lon2):
            if any(v is None for v in (lat1, lon1, lat2, lon2)):
                return 99999.0
            r = 6371.0
            phi1, phi2 = math.radians(float(lat1)), math.radians(float(lat2))
            dphi = math.radians(float(lat2) - float(lat1))
            dlambda = math.radians(float(lon2) - float(lon1))
            a = math.sin(dphi / 2.0)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2.0)**2
            c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
            return r * c

        try:
            dbapi_connection.create_function("haversine_km", 4, haversine_km)
            dbapi_connection.create_function("acos", 1, math.acos)
            dbapi_connection.create_function("cos", 1, math.cos)
            dbapi_connection.create_function("sin", 1, math.sin)
            dbapi_connection.create_function("radians", 1, math.radians)
        except Exception:
            pass

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """FastAPI dependency for database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
