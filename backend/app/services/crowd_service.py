"""
BUSMITRA - Centralized Crowd & Occupancy Monitoring Service
Unifies all occupancy calculations, thresholds and data formats across APIs.
"""
from typing import Dict, Any
from sqlalchemy.orm import Session
from app.models import Bus, PassengerCount, SensorStatus
from app.utils.calculations import calculate_occupancy_metrics

class CrowdService:
    @staticmethod
    def get_bus_occupancy(db: Session, bus: Bus) -> Dict[str, Any]:
        latest_count = (
            db.query(PassengerCount)
            .filter(PassengerCount.bus_id == bus.id)
            .order_by(PassengerCount.recorded_at.desc(), PassengerCount.id.desc())
            .first()
        )
        latest_sensor = (
            db.query(SensorStatus)
            .filter(SensorStatus.bus_id == bus.id)
            .first()
        )

        in_count = latest_count.in_count if latest_count else 0
        out_count = latest_count.out_count if latest_count else 0
        source_type = latest_count.source_type if latest_count else "SIMULATED"

        metrics = calculate_occupancy_metrics(bus.capacity, in_count, out_count)
        sensor_status = latest_sensor.sensor_status if latest_sensor else "CONNECTED"

        return {
            "bus_id": bus.id,
            "busId": bus.id,
            "bus_number": bus.bus_number,
            "capacity": metrics["capacity"],
            "total_in": metrics["total_in"],
            "total_out": metrics["total_out"],
            "sensorInCount": metrics["total_in"],
            "sensorOutCount": metrics["total_out"],
            "current_passengers": metrics["current_passengers"],
            "currentPassengers": metrics["current_passengers"],
            "available_seats": metrics["available_seats"],
            "availableSeats": metrics["available_seats"],
            "occupancy_percentage": metrics["occupancy_percentage"],
            "occupancyPercent": metrics["occupancy_percentage"],
            "crowd_level": metrics["crowd_level"],
            "crowdLevel": metrics["crowd_level"],
            "sensor_status": sensor_status,
            "sensorStatus": sensor_status,
            "last_updated": latest_count.recorded_at.isoformat() if latest_count else "Just now",
            "lastUpdated": latest_count.recorded_at.isoformat() if latest_count else "Just now",
            "data_source": "Directional IR Sensors (ESP32)" if source_type == "ESP32_IR" else "SIMULATED DEMO DATA",
            "is_simulated": source_type == "SIMULATED"
        }

crowd_service = CrowdService()
