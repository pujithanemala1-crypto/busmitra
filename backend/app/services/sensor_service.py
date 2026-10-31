"""
BUSMITRA - IR Sensor & Passenger Counting Service
Processes bi-directional entrance/exit IR beam pulses from ESP32 microcontrollers.
Supports incremental and cumulative counts, idempotency deduplication,
validates against negative passenger counts, and logs sensor connectivity.
"""
from datetime import datetime, timedelta
from typing import Dict, Any, Tuple
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models import Bus, PassengerCount, IRSensorEvent, SensorStatus
from app.config import settings
from app.utils.calculations import calculate_occupancy_metrics
from app.websocket.manager import ws_manager

class SensorService:
    @staticmethod
    def process_passenger_event(
        db: Session,
        bus: Bus,
        event_id: str | None = None,
        event_type: str | None = None, # "IN" or "OUT"
        in_delta: int = 0,
        out_delta: int = 0,
        is_cumulative: bool = False,
        cumulative_in: int | None = None,
        cumulative_out: int | None = None,
        device_id: str = "ESP32_DEFAULT",
        source_type: str = "ESP32_IR",
        recorded_at: datetime | None = None
    ) -> Tuple[PassengerCount, Dict[str, Any]]:
        # 1. Idempotency Check: Prevent duplicate event processing
        if event_id:
            existing = db.query(PassengerCount).filter(PassengerCount.event_id == event_id).first()
            if existing:
                metrics = calculate_occupancy_metrics(bus.capacity, existing.in_count, existing.out_count)
                return existing, metrics

        # 2. Retrieve Latest Stored Passenger Count
        latest = (
            db.query(PassengerCount)
            .filter(PassengerCount.bus_id == bus.id)
            .order_by(PassengerCount.recorded_at.desc(), PassengerCount.id.desc())
            .first()
        )
        current_in = latest.in_count if latest else 0
        current_out = latest.out_count if latest else 0
        current_onboard = max(0, current_in - current_out)

        # 3. Handle Cumulative vs Incremental
        if is_cumulative and cumulative_in is not None and cumulative_out is not None:
            if cumulative_out > cumulative_in:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid cumulative count: Total OUT count ({cumulative_out}) exceeds total IN count ({cumulative_in}). Passenger count cannot be negative."
                )
            if cumulative_in < current_in or cumulative_out < current_out:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid cumulative count: cumulative sensor values cannot decrease without hardware calibration reset."
                )
            new_in = cumulative_in
            new_out = cumulative_out
        else:
            # Incremental updates
            if event_type:
                evt_upper = event_type.strip().upper()
                if evt_upper == "IN":
                    in_delta = 1
                    out_delta = 0
                elif evt_upper == "OUT":
                    in_delta = 0
                    out_delta = 1

            if out_delta > current_onboard and in_delta == 0:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid sensor telemetry: OUT count ({out_delta}) exceeds current passengers onboard ({current_onboard}). Passenger count cannot be negative."
                )

            new_in = current_in + max(0, in_delta)
            new_out = current_out + max(0, out_delta)

        # 4. Strict Validation: OUT count cannot exceed IN count
        if new_out > new_in:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid sensor telemetry: Total OUT count ({new_out}) exceeds total IN count ({new_in}). Passenger count cannot be negative."
            )

        # 5. Compute Occupancy Metrics
        metrics = calculate_occupancy_metrics(bus.capacity, new_in, new_out)
        rec_time = recorded_at or datetime.utcnow()

        # 6. Save Record
        p_count = PassengerCount(
            bus_id=bus.id,
            in_count=new_in,
            out_count=new_out,
            current_passengers=metrics["current_passengers"],
            available_seats=metrics["available_seats"],
            occupancy_percentage=metrics["occupancy_percentage"],
            event_id=event_id,
            recorded_at=rec_time,
            source_type=source_type
        )
        db.add(p_count)

        # 6b. Log Raw IR Sensor Event
        direction = "IN" if in_delta > 0 or (is_cumulative and (cumulative_in or 0) > current_in) else "OUT"
        delta = max(1, in_delta if direction == "IN" else max(1, out_delta))
        ir_evt = IRSensorEvent(
            bus_id=bus.id,
            device_id=device_id,
            event_id=event_id,
            direction=direction,
            delta_count=delta,
            recorded_at=rec_time,
            raw_payload=f'{{"source": "{source_type}", "cumulative": {str(is_cumulative).lower()}, "in": {new_in}, "out": {new_out}}}'
        )
        db.add(ir_evt)

        # 7. Update Sensor Status
        s_status = (
            db.query(SensorStatus)
            .filter(SensorStatus.bus_id == bus.id)
            .first()
        )
        if not s_status:
            s_status = SensorStatus(
                bus_id=bus.id,
                esp32_device_id=device_id,
                sensor_status="CONNECTED",
                last_received_at=rec_time
            )
            db.add(s_status)
        else:
            s_status.esp32_device_id = device_id
            s_status.sensor_status = "CONNECTED"
            s_status.last_received_at = rec_time

        db.commit()
        db.refresh(p_count)

        return p_count, metrics

    @staticmethod
    def get_sensor_status(db: Session, bus: Bus) -> Dict[str, Any]:
        latest_sensor = (
            db.query(SensorStatus)
            .filter(SensorStatus.bus_id == bus.id)
            .order_by(SensorStatus.last_received_at.desc())
            .first()
        )
        latest_count = (
            db.query(PassengerCount)
            .filter(PassengerCount.bus_id == bus.id)
            .order_by(PassengerCount.recorded_at.desc())
            .first()
        )

        device_id = latest_sensor.esp32_device_id if latest_sensor else f"ESP32_BUS_{bus.id}"
        last_time = latest_sensor.last_received_at if latest_sensor else None

        # Calculate timeout: Disconnected if no packet received within SENSOR_TIMEOUT_SECONDS
        if last_time:
            is_active = (datetime.utcnow() - last_time) <= timedelta(seconds=settings.SENSOR_TIMEOUT_SECONDS)
            connection_status = "CONNECTED" if is_active else "DISCONNECTED"
        else:
            connection_status = "WAITING_FOR_DATA"

        total_in = latest_count.in_count if latest_count else 0
        total_out = latest_count.out_count if latest_count else 0

        return {
            "bus_id": bus.id,
            "esp32_device_id": device_id,
            "connection_status": connection_status,
            "last_received_at": last_time,
            "total_in": total_in,
            "total_out": total_out,
            "is_simulated": latest_count.source_type == "SIMULATED" if latest_count else True
        }

sensor_service = SensorService()
