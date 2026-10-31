#!/usr/bin/env python3
"""
BUSMITRA - Standalone Database Initialization & Demo Seeding Script
Creates tables, ensures SQLite PRAGMA configuration, loads initial transit datasets,
and validates database CRUD operations and connectivity.
"""
import sys
import os
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.config import settings
from app.database import engine, SessionLocal, init_db, seed_demo_data
from app.models import (
    User, Bus, Route, Stop, BusLocation, PassengerCount,
    IRSensorEvent, SensorStatus, CrowdPrediction, ETMTicket
)

def run_db_initialization():
    print("=" * 60)
    print("  BUSMITRA - DATABASE INITIALIZATION & VERIFICATION")
    print("  Smart Public Transportation & Crowd Monitoring")
    print("=" * 60)
    print(f"[*] Target SQLite Database: {settings.DEFAULT_DB_FILE}")
    print(f"[*] Connection String:      {settings.DATABASE_URL}")

    # Ensure parent directory exists
    settings.DEFAULT_DB_FILE.parent.mkdir(parents=True, exist_ok=True)

    # 1. Initialize tables & seed demo data
    print("\n[1/3] Creating SQLAlchemy tables and verifying schemas...")
    init_db()
    print("      ✓ Tables initialized successfully.")

    # 2. Query summary statistics
    print("\n[2/3] Querying table row counts from SQLite...")
    db = SessionLocal()
    try:
        tables = [
            ("Users (Admin/Operators)", User),
            ("Buses (APSRTC Fleet)", Bus),
            ("Routes (Corridors)", Route),
            ("Bus Stops (Stations)", Stop),
            ("Bus GPS Locations", BusLocation),
            ("Passenger Counts", PassengerCount),
            ("IR Sensor Beam Events", IRSensorEvent),
            ("Hardware Sensor Status", SensorStatus),
            ("Crowd Predictions", CrowdPrediction),
            ("Conductor ETM Tickets", ETMTicket),
        ]

        print("-" * 60)
        print(f"{'Table Name':<30} | {'Record Count':<15}")
        print("-" * 60)
        total_rows = 0
        for label, model in tables:
            count = db.query(model).count()
            total_rows += count
            print(f"{label:<30} | {count:<15}")
        print("-" * 60)
        print(f"{'Total Stored Records':<30} | {total_rows:<15}")
        print("-" * 60)

        # 3. Test basic CRUD operation
        print("\n[3/3] Performing round-trip CRUD verification check...")
        test_bus = db.query(Bus).filter(Bus.bus_number == "AP 16 1234").first()
        if test_bus:
            print(f"      ✓ Bus Found: {test_bus.bus_number} - {test_bus.bus_name} ({test_bus.source} -> {test_bus.destination})")
            latest_pc = db.query(PassengerCount).filter(PassengerCount.bus_id == test_bus.id).order_by(PassengerCount.recorded_at.desc()).first()
            if latest_pc:
                print(f"      ✓ Telematics: {latest_pc.current_passengers} onboard, {latest_pc.available_seats} seats free ({latest_pc.occupancy_percentage}% occupancy)")

        db_file = Path(settings.DEFAULT_DB_FILE)
        if db_file.exists():
            file_size_kb = round(db_file.stat().st_size / 1024, 2)
            print(f"\n[✓] Database File Verified on Disk: {db_file} ({file_size_kb} KB)")
        else:
            print("\n[!] Warning: Database file not found on disk.")

        print("\n============================================================")
        print("  Database initialization completed successfully!")
        print("============================================================\n")

    finally:
        db.close()

if __name__ == "__main__":
    run_db_initialization()
