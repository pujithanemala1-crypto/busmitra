"""
BUSMITRA - GPS & Location Telematics Service
Handles recording bus positions from Driver Phones, Dedicated GPS Hardware, or Simulation.
Maintains history and broadcasts updates to WebSocket clients.
"""
from datetime import datetime
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.models import Bus, BusLocation
from app.schemas import LocationCreate

class GPSService:
    @staticmethod
    def record_location(
        db: Session,
        bus: Bus,
        loc_in: LocationCreate
    ) -> BusLocation:
        rec_time = loc_in.recorded_at or datetime.utcnow()
        loc = BusLocation(
            bus_id=bus.id,
            latitude=loc_in.latitude,
            longitude=loc_in.longitude,
            speed=loc_in.speed,
            source_type=loc_in.source_type,
            recorded_at=rec_time
        )
        db.add(loc)

        # Update bus current coordinates
        bus.current_latitude = loc_in.latitude
        bus.current_longitude = loc_in.longitude
        bus.speed = loc_in.speed
        if loc_in.location_name:
            bus.current_location_name = loc_in.location_name

        db.commit()
        db.refresh(loc)
        return loc

    @staticmethod
    def get_latest_location(db: Session, bus: Bus) -> Dict[str, Any]:
        latest = (
            db.query(BusLocation)
            .filter(BusLocation.bus_id == bus.id)
            .order_by(BusLocation.recorded_at.desc(), BusLocation.id.desc())
            .first()
        )
        lat = latest.latitude if latest else bus.current_latitude or 16.5062
        lng = latest.longitude if latest else bus.current_longitude or 80.6480
        speed = latest.speed if latest else bus.speed
        source_type = latest.source_type if latest else "SIMULATED"
        recorded_at = latest.recorded_at if latest else datetime.utcnow()

        return {
            "bus_id": bus.id,
            "busId": bus.id,
            "bus_number": bus.bus_number,
            "latitude": lat,
            "longitude": lng,
            "lat": lat,
            "lng": lng,
            "current_location_name": bus.current_location_name or "On Route",
            "currentLocationName": bus.current_location_name or "On Route",
            "speed": speed,
            "speed_kmh": speed,
            "speedKmH": speed,
            "recorded_at": recorded_at,
            "last_updated": recorded_at.isoformat(),
            "lastUpdated": recorded_at.isoformat(),
            "gps_status": "ACTIVE",
            "source_type": source_type,
            "is_simulated": source_type == "SIMULATED",
            "isSimulated": source_type == "SIMULATED"
        }

    @staticmethod
    def get_location_history(db: Session, bus: Bus, limit: int = 50) -> List[Dict[str, Any]]:
        history = (
            db.query(BusLocation)
            .filter(BusLocation.bus_id == bus.id)
            .order_by(BusLocation.recorded_at.desc(), BusLocation.id.desc())
            .limit(limit)
            .all()
        )
        return [
            {
                "latitude": h.latitude,
                "longitude": h.longitude,
                "speed": h.speed,
                "source_type": h.source_type,
                "recorded_at": h.recorded_at
            }
            for h in history
        ]

gps_service = GPSService()
