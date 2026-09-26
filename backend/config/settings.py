"""
FIREGUARD AI - Global Application Configuration
SIH Problem Statement SIH26162
"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field

WORKSPACE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE = WORKSPACE_DIR / ".env"

class Settings(BaseSettings):
    # Server network settings
    PORT: int = Field(default=5000, validation_alias="PORT")
    HOST: str = Field(default="0.0.0.0", validation_alias="HOST")
    DEBUG: bool = Field(default=False, validation_alias="DEBUG")
    PROJECT_NAME: str = "FIREGUARD AI"
    VERSION: str = "2.0.0"
    PROBLEM_STATEMENT: str = "SIH26162 - Industrial Fire & Persistent Thermal Source Detection"

    # Operating Mode
    DEMO_MODE: bool = Field(default=False, validation_alias="DEMO_MODE")

    # NASA FIRMS API (supports both NASA_FIRMS_API_KEY and FIRMS_MAP_KEY)
    NASA_FIRMS_API_KEY: str = Field(default="", validation_alias="NASA_FIRMS_API_KEY")
    FIRMS_MAP_KEY: str = Field(default="", validation_alias="FIRMS_MAP_KEY")
    FIRMS_DEFAULT_SOURCE: str = Field(default="VIIRS_SNPP_NRT", validation_alias="FIRMS_DEFAULT_SOURCE")
    FIRMS_DEFAULT_COUNTRY: str = Field(default="IND", validation_alias="FIRMS_DEFAULT_COUNTRY")

    # OpenStreetMap Overpass API
    OSM_API_URL: str = Field(default="https://overpass-api.de/api/interpreter", validation_alias="OSM_API_URL")
    OVERPASS_ENDPOINT: str = Field(default="https://overpass-api.de/api/interpreter", validation_alias="OVERPASS_ENDPOINT")

    # External Provider Keys (optional)
    ROUTING_API_KEY: str = Field(default="", validation_alias="ROUTING_API_KEY")
    WEATHER_API_KEY: str = Field(default="", validation_alias="WEATHER_API_KEY")
    TWILIO_ACCOUNT_SID: str = Field(default="", validation_alias="TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN: str = Field(default="", validation_alias="TWILIO_AUTH_TOKEN")
    TWILIO_PHONE_NUMBER: str = Field(default="", validation_alias="TWILIO_PHONE_NUMBER")

    # Database
    DATABASE_URL: str = Field(default="sqlite:///backend/data/fireguard.db", validation_alias="DATABASE_URL")

    # Security & JWT
    JWT_SECRET: str = Field(default="fireguard_tactical_jwt_secret_sih2026_key_secure_99", validation_alias="JWT_SECRET")
    SECRET_KEY: str = Field(default="fireguard_tactical_jwt_secret_sih2026_key_secure_99", validation_alias="SECRET_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # Configurable Risk Thresholds (Requirement 8)
    RISK_THRESHOLD_LOW_MAX: int = 25
    RISK_THRESHOLD_MODERATE_MAX: int = 50
    RISK_THRESHOLD_HIGH_MAX: int = 75
    RISK_THRESHOLD_CRITICAL_MIN: int = 76

    class Config:
        env_file = str(ENV_FILE)
        env_file_encoding = "utf-8"
        extra = "ignore"

    @property
    def effective_firms_key(self) -> str:
        return self.NASA_FIRMS_API_KEY or self.FIRMS_MAP_KEY or ""

    @property
    def effective_osm_url(self) -> str:
        return self.OSM_API_URL or self.OVERPASS_ENDPOINT or "https://overpass-api.de/api/interpreter"

    @property
    def effective_jwt_secret(self) -> str:
        return self.JWT_SECRET or self.SECRET_KEY or "fireguard_default_secret_99"

settings = Settings()
