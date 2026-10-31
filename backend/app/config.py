"""
BUSMITRA - Backend Application Configuration
Handles environment variables, CORS settings, database paths, and secrets.
Ensures SQLite database file consistently resolves to backend/data/busmitra.db.
"""
import os
from pathlib import Path
from typing import List, Union
from pydantic_settings import BaseSettings, SettingsConfigDict

# Base directory for backend project
BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DB_FILE = BASE_DIR / "data" / "busmitra.db"

class Settings(BaseSettings):
    PROJECT_NAME: str = "BusMitra"
    API_V1_STR: str = "/api"
    
    # SQLite Database Configuration
    DEFAULT_DB_FILE: Path = DEFAULT_DB_FILE
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{DEFAULT_DB_FILE}")
    
    # JWT & Auth
    SECRET_KEY: str = os.getenv("SECRET_KEY", "busmitra-super-secret-jwt-key-for-transit-system-change-in-prod")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440 # 24 hours
    
    # ESP32 Sensor Security
    SENSOR_API_KEY: str = os.getenv("SENSOR_API_KEY", "bm-esp32-secret-key-2026")
    SENSOR_TIMEOUT_SECONDS: int = 120
    
    # CORS
    CORS_ORIGINS: Union[str, List[str]] = ["*"]
    
    # Crowd Density Thresholds (Percentages)
    CROWD_LOW_THRESHOLD: float = 40.0
    CROWD_MOD_THRESHOLD: float = 75.0
    CROWD_HIGH_THRESHOLD: float = 100.0
    
    # Demo Mode
    DEMO_MODE: bool = True

    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=".env",
        extra="allow"
    )

settings = Settings()
