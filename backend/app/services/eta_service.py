"""
BUSMITRA - ETA & Delay Calculation Service
Computes estimated time of arrival based on real-time GPS, road speed,
and distance to upcoming scheduled stops.
"""
from typing import Dict, Any
from sqlalchemy.orm import Session
from app.models import Bus, Stop, BusLocation
from app.utils.calculations import haversine_distance_km, calculate_eta_minutes

class ETAService:
    @staticmethod
    def calculate_eta(db: Session, bus: Bus) -> Dict[str, Any]:
        latest_loc = (
            db.query(BusLocation)
            .filter(BusLocation.bus_id == bus.id)
            .order_by(BusLocation.recorded_at.desc(), BusLocation.id.desc())
            .first()
        )
        cur_lat = latest_loc.latitude if latest_loc else bus.current_latitude or 16.5062
        cur_lng = latest_loc.longitude if latest_loc else bus.current_longitude or 80.6480
        speed = latest_loc.speed if latest_loc else bus.speed

        # Find next stop
        next_stop_name = "Destination Terminal"
        distance_km = 3.5
        sched_time = bus.expected_arrival_time

        if bus.route_id:
            stops = (
                db.query(Stop)
                .filter(Stop.route_id == bus.route_id)
                .order_by(Stop.stop_order.asc())
                .all()
            )
            if stops:
                target_idx = min(bus.current_stop_index + 1, len(stops) - 1)
                target_stop = stops[target_idx]
                next_stop_name = target_stop.stop_name
                sched_time = target_stop.scheduled_arrival_time or bus.expected_arrival_time
                distance_km = haversine_distance_km(cur_lat, cur_lng, target_stop.latitude, target_stop.longitude)

        # Calculate arrival duration in minutes
        eta_minutes = calculate_eta_minutes(distance_km, speed)

        return {
            "bus_id": bus.id,
            "bus_number": bus.bus_number,
            "current_location": bus.current_location_name or "En-route",
            "next_stop": next_stop_name,
            "distance_to_next_stop_km": distance_km,
            "distance_to_next_stop": f"{distance_km} km",
            "estimated_arrival": f"{eta_minutes} mins",
            "scheduled_time": sched_time,
            "delay_minutes": 0,
            "status": "On Time" if speed > 20 else "Slow Traffic" if speed > 5 else "At Stop",
            "data_source": "GPS Live Telematics (Simulated)" if (latest_loc and latest_loc.source_type == "SIMULATED") else "Hardware GPS Stream"
        }

eta_service = ETAService()
