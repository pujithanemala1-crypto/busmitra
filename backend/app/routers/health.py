"""
BUSMITRA - Health Check Router
Endpoint for probers, monitoring consoles and system status verification.
"""
import os
import time
from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db
from app.models import Bus
from app.config import settings
from app.schemas import HealthResponse

router = APIRouter(prefix="", tags=["Health"])

@router.get("/api/health", response_model=HealthResponse)
def get_system_health(db: Session = Depends(get_db)):
    db_connected = False
    active_buses = 0
    try:
        db.execute(text("SELECT 1"))
        db_connected = True
        active_buses = db.query(Bus).filter(Bus.status == "ACTIVE").count()
    except Exception:
        db_connected = False

    return {
        "status": "HEALTHY" if db_connected else "DEGRADED",
        "database_connected": db_connected,
        "active_buses": active_buses,
        "demo_mode": settings.DEMO_MODE,
        "timestamp": datetime.utcnow()
    }

@router.get("/api/health/db")
def get_database_health(db: Session = Depends(get_db)):
    """
    Verifies SQLite database connectivity, pragma settings, file state,
    and returns registered tables and round-trip latency.
    """
    start_time = time.time()
    try:
        db.execute(text("SELECT 1")).scalar()
        ping_ms = round((time.time() - start_time) * 1000, 2)

        fk_status = db.execute(text("PRAGMA foreign_keys")).scalar()
        journal_mode = db.execute(text("PRAGMA journal_mode")).scalar()

        tables_res = db.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")).fetchall()
        table_names = [r[0] for r in tables_res]

        db_path = str(settings.DEFAULT_DB_FILE)
        file_exists = os.path.exists(db_path)
        file_size_bytes = os.path.getsize(db_path) if file_exists else 0

        return {
            "status": "CONNECTED",
            "database_engine": "SQLite",
            "database_path": db_path,
            "database_file_exists": file_exists,
            "database_size_bytes": file_size_bytes,
            "ping_ms": ping_ms,
            "foreign_keys_enabled": bool(fk_status == 1),
            "journal_mode": str(journal_mode).upper(),
            "table_count": len(table_names),
            "tables": table_names,
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        return {
            "status": "ERROR",
            "database_engine": "SQLite",
            "database_path": str(settings.DEFAULT_DB_FILE),
            "error": str(e),
            "timestamp": datetime.utcnow()
        }
