"""
FIREGUARD AI - Global Configuration
Supports dynamic environment overrides, NASA FIRMS API key, Overpass endpoint, and demo mode.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
WORKSPACE_DIR = BASE_DIR.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# Load environment variables from .env file in project root if present
load_dotenv(WORKSPACE_DIR / ".env")

class Config:
    PROJECT_NAME = "FIREGUARD AI"
    VERSION = "1.0.0"
    PROBLEM_STATEMENT = "SIH26162 - AI-Based Detection and Classification of Industrial Fires & Persistent Thermal Sources"

    # Database
    DATABASE_PATH = DATA_DIR / "fireguard.db"
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", f"sqlite:///{DATABASE_PATH}")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Security
    SECRET_KEY = os.getenv("SECRET_KEY", "fireguard_tactical_jwt_secret_sih2026_key_secure_99")
    JWT_EXPIRATION_HOURS = 24

    # Demo Mode (Defaults to True for seamless out-of-the-box evaluation)
    DEMO_MODE = os.getenv("DEMO_MODE", "true").lower() in ("true", "1", "yes")

    # NASA FIRMS API
    # Evaluators can supply their FIRMS MAP_KEY via environment variable or in Settings UI
    FIRMS_MAP_KEY = os.getenv("FIRMS_MAP_KEY", "")
    FIRMS_API_BASE = "https://firms.modaps.eosdis.nasa.gov/api"
    FIRMS_DEFAULT_SOURCE = "VIIRS_SNPP_NRT"  # MODIS_NRT, VIIRS_SNPP_NRT, VIIRS_NOAA20_NRT, VIIRS_NOAA21_NRT
    FIRMS_DEFAULT_COUNTRY = "IND"

    # OpenStreetMap / Overpass API
    OVERPASS_ENDPOINT = os.getenv("OVERPASS_ENDPOINT", "https://overpass-api.de/api/interpreter")

    # Server Defaults
    HOST = os.getenv("HOST", "127.0.0.1")
    PORT = int(os.getenv("PORT", 5000))
    DEBUG = os.getenv("DEBUG", "false").lower() in ("true", "1")
