"""
FIREGUARD AI - Database Engine and Spatial Support
Configures SQLAlchemy with SQLite (out-of-the-box zero-setup) and custom spatial functions.
"""
import math
import sqlite3
from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import Config

# Connect to database
engine = create_engine(
    Config.SQLALCHEMY_DATABASE_URI,
    connect_args={"check_same_thread": False} if "sqlite" in Config.SQLALCHEMY_DATABASE_URI else {}
)

# Register Spatial math functions in SQLite connection
@event.listens_for(engine, "connect")
def connect(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, sqlite3.Connection):
        dbapi_connection.create_function("sin", 1, math.sin)
        dbapi_connection.create_function("cos", 1, math.cos)
        dbapi_connection.create_function("sqrt", 1, math.sqrt)
        dbapi_connection.create_function("radians", 1, math.radians)
        dbapi_connection.create_function("atan2", 2, math.atan2)

        def haversine_km(lat1, lon1, lat2, lon2):
            if None in (lat1, lon1, lat2, lon2):
                return None
            R = 6371.0 # Earth radius in km
            dlat = math.radians(lat2 - lat1)
            dlon = math.radians(lon2 - lon1)
            a = (math.sin(dlat / 2.0) ** 2 +
                 math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
                 math.sin(dlon / 2.0) ** 2)
            c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
            return R * c

        dbapi_connection.create_function("haversine_km", 4, haversine_km)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
