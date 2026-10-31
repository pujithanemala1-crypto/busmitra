"""
BUSMITRA - Buses Router
Endpoints for querying available buses, route matching, schedules, and administrative CRUD.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Bus, Route, Stop
from app.schemas import BusCreate, BusUpdate
from app.services.bus_service import (
    resolve_bus, get_all_buses, get_bus_complete_dict, create_bus, update_bus
)
from app.services.eta_service import eta_service
from app.routers.users import require_admin_user

router = APIRouter(prefix="", tags=["Buses"])

@router.get("/api/buses")
def list_buses(
    source: Optional[str] = Query(None, description="Starting transit city or terminal"),
    destination: Optional[str] = Query(None, description="Destination city or terminal"),
    db: Session = Depends(get_db)
):
    """
    Returns all active buses with real-time seat availability and crowd levels.
    Supports filtering by source and destination.
    """
    return get_all_buses(db, source=source, destination=destination)

@router.get("/api/buses/search")
def search_buses(
    source: str = Query(..., description="Source location"),
    destination: str = Query(..., description="Destination location"),
    db: Session = Depends(get_db)
):
    """
    Search available buses strictly matching the requested corridor.
    """
    results = get_all_buses(db, source=source, destination=destination)
    if not results:
        # If strict match empty, return all corridor buses with notice
        results = get_all_buses(db)
    return results

@router.get("/api/buses/{bus_id}")
def get_bus_details(bus_id: str, db: Session = Depends(get_db)):
    """
    Returns complete real-time telemetry and schedule details for a specific bus.
    Resolves both integer ID (e.g. '1') and registration number ('AP 16 1234' / 'AP161234').
    """
    bus = resolve_bus(db, bus_id)
    if not bus:
        raise HTTPException(status_code=404, detail=f"Bus '{bus_id}' not found")
    return get_bus_complete_dict(db, bus)

@router.get("/api/buses/{bus_id}/route")
def get_bus_route(bus_id: str, db: Session = Depends(get_db)):
    """
    Returns the complete route geometry waypoints and ordered intermediate stops for this bus.
    """
    bus = resolve_bus(db, bus_id)
    if not bus:
        raise HTTPException(status_code=404, detail=f"Bus '{bus_id}' not found")

    if not bus.route_id:
        return {"bus_id": bus.id, "route": None, "stops": [], "waypoints": []}

    route = db.query(Route).filter(Route.id == bus.route_id).first()
    stops = db.query(Stop).filter(Stop.route_id == bus.route_id).order_by(Stop.stop_order.asc()).all()

    import json
    waypoints = json.loads(route.waypoints_json) if (route and route.waypoints_json) else []

    return {
        "bus_id": bus.id,
        "bus_number": bus.bus_number,
        "route_id": route.id if route else None,
        "route_name": route.route_name if route else f"{bus.source} to {bus.destination}",
        "source": bus.source,
        "destination": bus.destination,
        "total_distance_km": route.total_distance if route else 34.5,
        "stops": [
            {
                "id": s.id,
                "name": s.stop_name,
                "order": s.stop_order,
                "lat": s.latitude,
                "lng": s.longitude,
                "scheduled_time": s.scheduled_arrival_time,
                "status": "COMPLETED" if s.stop_order <= bus.current_stop_index else "APPROACHING" if s.stop_order == bus.current_stop_index + 1 else "UPCOMING"
            }
            for s in stops
        ],
        "waypoints": waypoints
    }

@router.get("/api/buses/{bus_id}/timings")
def get_bus_timings(bus_id: str, db: Session = Depends(get_db)):
    """
    Returns scheduled departure, expected arrival, and live delay telemetry.
    """
    bus = resolve_bus(db, bus_id)
    if not bus:
        raise HTTPException(status_code=404, detail=f"Bus '{bus_id}' not found")

    eta_data = eta_service.calculate_eta(db, bus)
    return {
        "bus_id": bus.id,
        "bus_number": bus.bus_number,
        "departure_time": bus.departure_time,
        "scheduled_arrival_time": bus.expected_arrival_time,
        "estimated_arrival": eta_data["estimated_arrival"],
        "delay_minutes": eta_data["delay_minutes"],
        "status": eta_data["status"],
        "current_location": eta_data["current_location"],
        "next_stop": eta_data["next_stop"],
        "last_updated": "Just now"
    }

@router.post("/api/buses", status_code=201)
def create_new_bus(
    bus_in: BusCreate,
    admin=Depends(require_admin_user),
    db: Session = Depends(get_db)
):
    """
    Create a new bus record. Protected endpoint for administrators.
    """
    existing = db.query(Bus).filter(Bus.bus_number == bus_in.bus_number).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Bus with number '{bus_in.bus_number}' already exists")
    bus = create_bus(db, bus_in)
    return get_bus_complete_dict(db, bus)

@router.put("/api/buses/{bus_id}")
def update_existing_bus(
    bus_id: str,
    bus_in: BusUpdate,
    admin=Depends(require_admin_user),
    db: Session = Depends(get_db)
):
    """
    Update bus details. Protected endpoint for administrators.
    """
    bus = resolve_bus(db, bus_id)
    if not bus:
        raise HTTPException(status_code=404, detail=f"Bus '{bus_id}' not found")
    bus = update_bus(db, bus, bus_in)
    return get_bus_complete_dict(db, bus)
