"""
BUSMITRA - GPS Live Tracking Router
Endpoints for real-time bus coordinates ingestion, location history,
ETA calculations and WebSocket telematics broadcast.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import LocationCreate, LocationResponse
from app.services.bus_service import resolve_bus
from app.services.gps_service import gps_service
from app.services.eta_service import eta_service
from app.websocket.manager import ws_manager

router = APIRouter(prefix="", tags=["GPS Tracking & Telematics"])

@router.post("/api/buses/{bus_id}/location", status_code=200)
async def post_bus_location(
    bus_id: str,
    loc_in: LocationCreate,
    db: Session = Depends(get_db)
):
    """
    Ingest GPS coordinates from Driver smartphone, dedicated GPS tracker, or simulator.
    Saves to database and broadcasts BUS_LOCATION_UPDATED and ETA_UPDATED over WebSocket.
    """
    bus = resolve_bus(db, bus_id)
    if not bus:
        raise HTTPException(status_code=404, detail=f"Bus '{bus_id}' not found")

    loc = gps_service.record_location(db, bus, loc_in)
    loc_data = gps_service.get_latest_location(db, bus)
    eta_data = eta_service.calculate_eta(db, bus)

    # Broadcast via WebSocket
    await ws_manager.broadcast_to_bus(str(bus.id), "BUS_LOCATION_UPDATED", loc_data)
    await ws_manager.broadcast_to_bus(bus.bus_number, "BUS_LOCATION_UPDATED", loc_data)
    await ws_manager.broadcast_to_bus(str(bus.id), "ETA_UPDATED", eta_data)
    await ws_manager.broadcast_to_bus(bus.bus_number, "ETA_UPDATED", eta_data)

    return {
        "success": True,
        "location": loc_data,
        "eta": eta_data
    }

@router.get("/api/buses/{bus_id}/location")
def get_bus_location(bus_id: str, db: Session = Depends(get_db)):
    """
    Retrieve current latitude, longitude, speed, location name, and GPS status.
    """
    bus = resolve_bus(db, bus_id)
    if not bus:
        raise HTTPException(status_code=404, detail=f"Bus '{bus_id}' not found")
    return gps_service.get_latest_location(db, bus)

@router.get("/api/buses/{bus_id}/location/history")
def get_bus_location_history(
    bus_id: str,
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """
    Retrieve historical GPS coordinate breadcrumbs for the selected bus.
    """
    bus = resolve_bus(db, bus_id)
    if not bus:
        raise HTTPException(status_code=404, detail=f"Bus '{bus_id}' not found")
    return {
        "bus_id": bus.id,
        "bus_number": bus.bus_number,
        "history": gps_service.get_location_history(db, bus, limit=limit)
    }

@router.get("/api/buses/{bus_id}/eta")
def get_bus_eta(bus_id: str, db: Session = Depends(get_db)):
    """
    Calculates dynamic ETA and delay information based on remaining distance and speed.
    """
    bus = resolve_bus(db, bus_id)
    if not bus:
        raise HTTPException(status_code=404, detail=f"Bus '{bus_id}' not found")
    return eta_service.calculate_eta(db, bus)
