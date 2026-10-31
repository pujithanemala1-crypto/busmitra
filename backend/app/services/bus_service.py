"""
BUSMITRA - Bus Management Service
Business logic for bus retrieval, route filtering, status updates and formatting.
"""
from typing import List, Optional, Any
from sqlalchemy.orm import Session
from app.models import Bus, PassengerCount, BusLocation, SensorStatus
from app.schemas import BusCreate, BusUpdate
from app.utils.calculations import calculate_occupancy_metrics

def resolve_bus(db: Session, bus_identifier: Any) -> Optional[Bus]:
    """
    Resolves a bus either by integer ID or by formatted / unformatted registration number.
    e.g. "1", 1, "AP 16 1234", "AP161234".
    """
    if bus_identifier is None:
        return None

    # Try numeric ID
    if isinstance(bus_identifier, int) or (isinstance(bus_identifier, str) and bus_identifier.isdigit()):
        bus = db.query(Bus).filter(Bus.id == int(bus_identifier)).first()
        if bus:
            return bus

    clean_str = str(bus_identifier).replace(" ", "").upper()
    buses = db.query(Bus).all()
    for b in buses:
        if b.bus_number.replace(" ", "").upper() == clean_str:
            return b
    return None

def get_all_buses(db: Session, source: Optional[str] = None, destination: Optional[str] = None) -> List[dict]:
    query = db.query(Bus)
    if source:
        query = query.filter(Bus.source.ilike(f"%{source.strip()}%"))
    if destination:
        query = query.filter(Bus.destination.ilike(f"%{destination.strip()}%"))

    buses = query.all()
    results = []
    for bus in buses:
        results.append(get_bus_complete_dict(db, bus))
    return results

def get_bus_complete_dict(db: Session, bus: Bus) -> dict:
    """
    Assembles complete real-time state for a bus matching both frontend and API expectations.
    """
    # Latest passenger counts
    latest_count = (
        db.query(PassengerCount)
        .filter(PassengerCount.bus_id == bus.id)
        .order_by(PassengerCount.recorded_at.desc(), PassengerCount.id.desc())
        .first()
    )
    in_c = latest_count.in_count if latest_count else 0
    out_c = latest_count.out_count if latest_count else 0
    metrics = calculate_occupancy_metrics(bus.capacity, in_c, out_c)

    # Latest location
    latest_loc = (
        db.query(BusLocation)
        .filter(BusLocation.bus_id == bus.id)
        .order_by(BusLocation.recorded_at.desc(), BusLocation.id.desc())
        .first()
    )
    current_lat = latest_loc.latitude if latest_loc else bus.current_latitude
    current_lng = latest_loc.longitude if latest_loc else bus.current_longitude
    speed = latest_loc.speed if latest_loc else bus.speed

    # Latest sensor status
    latest_sensor = (
        db.query(SensorStatus)
        .filter(SensorStatus.bus_id == bus.id)
        .order_by(SensorStatus.last_received_at.desc())
        .first()
    )
    sensor_st = latest_sensor.sensor_status if latest_sensor else "CONNECTED"

    return {
        "id": bus.id,
        "bus_id": bus.id,
        "number": bus.bus_number,
        "bus_number": bus.bus_number,
        "name": bus.bus_name,
        "bus_name": bus.bus_name,
        "serviceType": bus.service_type,
        "service_type": bus.service_type,
        "capacity": bus.capacity,
        "source": bus.source,
        "destination": bus.destination,
        "departureTime": bus.departure_time,
        "departure_time": bus.departure_time,
        "expectedArrivalTime": bus.expected_arrival_time,
        "expected_arrival_time": bus.expected_arrival_time,
        "route_id": bus.route_id,
        "current_latitude": current_lat,
        "current_longitude": current_lng,
        "lat": current_lat,
        "lng": current_lng,
        "current_location_name": bus.current_location_name,
        "currentLocationName": bus.current_location_name,
        "speed": speed,
        "current_stop_index": bus.current_stop_index,
        "status": bus.status,
        "current_passengers": metrics["current_passengers"],
        "currentPassengers": metrics["current_passengers"],
        "available_seats": metrics["available_seats"],
        "availableSeats": metrics["available_seats"],
        "occupancy_percent": metrics["occupancy_percentage"],
        "occupancyPercent": metrics["occupancy_percentage"],
        "crowd_level": metrics["crowd_level"],
        "crowdLevel": metrics["crowd_level"],
        "sensor_in_count": metrics["total_in"],
        "sensorInCount": metrics["total_in"],
        "sensor_out_count": metrics["total_out"],
        "sensorOutCount": metrics["total_out"],
        "sensorStatus": sensor_st,
        "gps_status": "ACTIVE",
        "gpsStatus": "ACTIVE",
        "last_updated": "Just now",
        "lastUpdated": "Just now",
        "created_at": bus.created_at,
        "updated_at": bus.updated_at
    }

def create_bus(db: Session, bus_in: BusCreate) -> Bus:
    bus = Bus(
        bus_number=bus_in.bus_number,
        bus_name=bus_in.bus_name,
        service_type=bus_in.service_type,
        capacity=bus_in.capacity,
        source=bus_in.source,
        destination=bus_in.destination,
        departure_time=bus_in.departure_time,
        expected_arrival_time=bus_in.expected_arrival_time,
        route_id=bus_in.route_id,
        status=bus_in.status
    )
    db.add(bus)
    db.commit()
    db.refresh(bus)
    return bus

def update_bus(db: Session, bus: Bus, bus_in: BusUpdate) -> Bus:
    for field, val in bus_in.model_dump(exclude_unset=True).items():
        setattr(bus, field, val)
    db.commit()
    db.refresh(bus)
    return bus
