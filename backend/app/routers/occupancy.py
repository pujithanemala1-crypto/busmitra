"""
BUSMITRA - Occupancy & Passenger Counting Router
Endpoints for real-time passenger counts, seat availability and crowd levels.
"""
from datetime import datetime
from typing import Optional, Any
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.bus_service import resolve_bus
from app.services.sensor_service import sensor_service
from app.services.crowd_service import crowd_service
from app.services.prediction_service import prediction_service
from app.websocket.manager import ws_manager

router = APIRouter(prefix="", tags=["Occupancy & Passenger Counting"])

@router.get("/api/buses/{bus_id}/occupancy")
def get_occupancy(bus_id: str, db: Session = Depends(get_db)):
    """
    Returns real-time occupancy percentage, available seats, and crowd level.
    """
    bus = resolve_bus(db, bus_id)
    if not bus:
        raise HTTPException(status_code=404, detail=f"Bus '{bus_id}' not found")
    return crowd_service.get_bus_occupancy(db, bus)

@router.post("/api/buses/{bus_id}/passenger-count", status_code=200)
async def post_passenger_count(
    bus_id: str,
    payload: dict = Body(..., json_schema_extra={"example": {"eventType": "IN"}}),
    db: Session = Depends(get_db)
):
    """
    Ingest passenger count update from frontend simulation or hardware gateway.
    Supports:
    - Incremental eventType ("IN" or "OUT")
    - Incremental in_count / out_count deltas
    - Cumulative in_count / out_count totals
    """
    bus = resolve_bus(db, bus_id)
    if not bus:
        raise HTTPException(status_code=404, detail=f"Bus '{bus_id}' not found")

    # Parse flexible inputs matching frontend & IoT payloads
    event_type = payload.get("eventType") or payload.get("event_type") or payload.get("direction")
    in_delta = int(payload.get("in_count", 0)) if not payload.get("is_cumulative") else 0
    out_delta = int(payload.get("out_count", 0)) if not payload.get("is_cumulative") else 0
    is_cumulative = bool(payload.get("is_cumulative", False))
    cumulative_in = int(payload["in_count"]) if (is_cumulative and "in_count" in payload) else None
    cumulative_out = int(payload["out_count"]) if (is_cumulative and "out_count" in payload) else None
    event_id = payload.get("event_id") or payload.get("eventId")
    device_id = payload.get("device_id") or payload.get("deviceId") or f"ESP32_BUS_{bus.id}"
    source_type = payload.get("source_type") or payload.get("sourceType") or "ESP32_IR"

    p_count, metrics = sensor_service.process_passenger_event(
        db=db,
        bus=bus,
        event_id=event_id,
        event_type=event_type,
        in_delta=in_delta,
        out_delta=out_delta,
        is_cumulative=is_cumulative,
        cumulative_in=cumulative_in,
        cumulative_out=cumulative_out,
        device_id=device_id,
        source_type=source_type,
        recorded_at=datetime.utcnow()
    )

    occ_data = crowd_service.get_bus_occupancy(db, bus)
    pred_data = prediction_service.get_crowd_prediction(db, bus)

    # Broadcast real-time updates over WebSocket
    for key in [str(bus.id), bus.bus_number]:
        await ws_manager.broadcast_to_bus(key, "OCCUPANCY_UPDATED", occ_data)
        await ws_manager.broadcast_to_bus(key, "CROWD_LEVEL_UPDATED", {
            "bus_id": bus.id,
            "crowd_level": metrics["crowd_level"],
            "occupancy_percentage": metrics["occupancy_percentage"],
            "available_seats": metrics["available_seats"]
        })
        await ws_manager.broadcast_to_bus(key, "CROWD_PREDICTION_UPDATED", pred_data)

    return {
        "success": True,
        "metrics": metrics,
        "occupancy": occ_data,
        "prediction": pred_data
    }
