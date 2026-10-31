"""
BUSMITRA - ESP32 Direct Sensor Protocol Router
Dedicated endpoint for physical ESP32 directional IR microcontrollers.
Includes API Key device authentication, idempotency deduplication and telemetry broadcasting.
"""
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.config import settings
from app.schemas import IRSensorEvent, SensorStatusResponse
from app.services.bus_service import resolve_bus
from app.services.sensor_service import sensor_service
from app.services.crowd_service import crowd_service
from app.websocket.manager import ws_manager

router = APIRouter(prefix="", tags=["ESP32 IR Sensors"])

def verify_sensor_api_key(x_api_key: Optional[str] = Header(None)):
    """
    Validates physical ESP32 device security header if configured.
    """
    if settings.SENSOR_API_KEY and x_api_key:
        if x_api_key != settings.SENSOR_API_KEY:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid IoT Device API Key"
            )
    return True

@router.post("/api/sensors/ir-data", status_code=200)
async def ingest_ir_sensor_event(
    event: IRSensorEvent,
    auth=Depends(verify_sensor_api_key),
    db: Session = Depends(get_db)
):
    """
    ESP32 Bi-Directional Infrared Sensor Gateway.
    - Direction "IN": Passenger boards (+1)
    - Direction "OUT": Passenger alights (-1)
    """
    bus = resolve_bus(db, event.bus_id)
    if not bus:
        raise HTTPException(status_code=404, detail=f"Target bus '{event.bus_id}' not found")

    p_count, metrics = sensor_service.process_passenger_event(
        db=db,
        bus=bus,
        event_id=event.event_id,
        event_type=event.direction,
        device_id=event.device_id,
        source_type="ESP32_IR",
        recorded_at=event.recorded_at or datetime.utcnow()
    )

    occ_data = crowd_service.get_bus_occupancy(db, bus)
    sensor_status_data = sensor_service.get_sensor_status(db, bus)

    # Broadcast telemetry
    for key in [str(bus.id), bus.bus_number]:
        await ws_manager.broadcast_to_bus(key, "OCCUPANCY_UPDATED", occ_data)
        await ws_manager.broadcast_to_bus(key, "SENSOR_STATUS_UPDATED", sensor_status_data)

    return {
        "success": True,
        "event_id": event.event_id,
        "direction": event.direction,
        "bus_id": bus.id,
        "current_passengers": metrics["current_passengers"],
        "available_seats": metrics["available_seats"],
        "occupancy_percentage": metrics["occupancy_percentage"],
        "crowd_level": metrics["crowd_level"],
        "recorded_at": p_count.recorded_at
    }

@router.get("/api/sensors/status/{bus_id}", response_model=SensorStatusResponse)
def get_sensor_connection_status(bus_id: str, db: Session = Depends(get_db)):
    """
    Returns live connectivity status, timeout check, and total pulse counts for the ESP32 module.
    """
    bus = resolve_bus(db, bus_id)
    if not bus:
        raise HTTPException(status_code=404, detail=f"Bus '{bus_id}' not found")
    return sensor_service.get_sensor_status(db, bus)
