"""
BUSMITRA - Database Engine, Session Management & Seeding
Configures SQLite with SQLAlchemy ORM and handles idempotent initial demo seeding.
"""
import os
import json
import hashlib
import hmac
from datetime import datetime
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session
from app.config import settings
from app.models import (
    Base, Bus, Route, Stop, BusLocation, PassengerCount,
    IRSensorEvent, SensorStatus, CrowdPrediction, ETMTicket, User
)
from app.utils.calculations import calculate_occupancy_metrics

def hash_password(password: str) -> str:
    salt = b"busmitra_salt_2026"
    pwd_bytes = password.encode("utf-8")
    derived = hashlib.pbkdf2_hmac("sha256", pwd_bytes, salt, 100000)
    return derived.hex()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return hmac.compare_digest(hash_password(plain_password), hashed_password)

# Ensure sqlite data directory exists
settings.DEFAULT_DB_FILE.parent.mkdir(parents=True, exist_ok=True)

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False, "timeout": 30} if "sqlite" in settings.DATABASE_URL else {}
)

# Enforce SQLite foreign keys and WAL journal mode for ACID compliance and concurrency
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if "sqlite" in settings.DATABASE_URL:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.execute("PRAGMA journal_mode=WAL;")
        cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

def seed_demo_data(db: Session):
    """
    Seeds initial routes, stops, buses, admin user, and telematics state.
    Strictly idempotent: does not overwrite or duplicate existing records.
    """
    # 1. Seed Admin User if none exists
    if not db.query(User).filter(User.username == "admin").first():
        admin = User(
            username="admin",
            email="admin@busmitra.gov.in",
            hashed_password=hash_password("admin123"),
            role="admin",
            is_active=True
        )
        db.add(admin)
        db.commit()

    # 2. Seed Routes & Stops if none exist
    if db.query(Route).count() == 0:
        # Route 1: Vijayawada to Guntur
        vja_gnt_waypoints = [
            [16.5062, 80.6480],
            [16.5120, 80.6650],
            [16.5186, 80.6860],
            [16.5280, 80.7450],
            [16.5369, 80.8037],
            [16.4950, 80.6900],
            [16.4812, 80.6053],
            [16.4520, 80.5820],
            [16.4357, 80.5645],
            [16.3750, 80.5100],
            [16.3300, 80.4650],
            [16.3067, 80.4365]
        ]

        route1 = Route(
            route_name="Vijayawada to Guntur Express Corridor",
            source="Vijayawada",
            destination="Guntur",
            total_distance=34.5,
            estimated_duration=75,
            waypoints_json=json.dumps(vja_gnt_waypoints)
        )
        db.add(route1)
        db.flush()

        # Stops for Route 1
        stops_data = [
            {"name": "Vijayawada (PNBS Bus Station)", "lat": 16.5062, "lng": 80.6480, "order": 1, "time": "10:30 AM"},
            {"name": "Enikepadu Junction", "lat": 16.5186, "lng": 80.6860, "order": 2, "time": "10:45 AM"},
            {"name": "Gannavaram Bypass", "lat": 16.5369, "lng": 80.8037, "order": 3, "time": "11:00 AM"},
            {"name": "Mangalagiri (AIIMS Bypass)", "lat": 16.4357, "lng": 80.5645, "order": 4, "time": "11:15 AM"},
            {"name": "Tadepalli Highway", "lat": 16.4812, "lng": 80.6053, "order": 5, "time": "11:30 AM"},
            {"name": "Guntur (NTR Bus Terminal)", "lat": 16.3067, "lng": 80.4365, "order": 6, "time": "11:45 AM"}
        ]
        for s in stops_data:
            stop = Stop(
                route_id=route1.id,
                stop_name=s["name"],
                stop_order=s["order"],
                latitude=s["lat"],
                longitude=s["lng"],
                scheduled_arrival_time=s["time"]
            )
            db.add(stop)

        # Route 2: Vijayawada to Mangalagiri
        route2 = Route(
            route_name="Vijayawada to Mangalagiri AIIMS Connect",
            source="Vijayawada",
            destination="Mangalagiri",
            total_distance=14.0,
            estimated_duration=35,
            waypoints_json=json.dumps([[16.5062, 80.6480], [16.4812, 80.6053], [16.4357, 80.5645]])
        )
        db.add(route2)

        # Route 3: Vijayawada to Gannavaram
        route3 = Route(
            route_name="Vijayawada to Gannavaram Airport Link",
            source="Vijayawada",
            destination="Gannavaram",
            total_distance=21.0,
            estimated_duration=45,
            waypoints_json=json.dumps([[16.5062, 80.6480], [16.5186, 80.6860], [16.5369, 80.8037]])
        )
        db.add(route3)
        db.commit()

    # 3. Seed Buses if none exist
    if db.query(Bus).count() == 0:
        route1 = db.query(Route).filter(Route.source == "Vijayawada", Route.destination == "Guntur").first()
        route_id = route1.id if route1 else 1

        buses_to_seed = [
            {
                "bus_number": "AP 16 1234",
                "bus_name": "Amaravati Express",
                "service_type": "Express",
                "capacity": 50,
                "source": "Vijayawada",
                "destination": "Guntur",
                "departure_time": "10:30 AM",
                "expected_arrival_time": "11:45 AM",
                "current_latitude": 16.4520,
                "current_longitude": 80.5820,
                "current_location_name": "Mangalagiri Highway (Km 18)",
                "speed": 52.0,
                "current_stop_index": 2,
                "in_count": 32,
                "out_count": 7,
                "device_id": "ESP32_BUS_001",
                "prediction": {
                    "next_stop": "Mangalagiri (AIIMS Bypass)",
                    "expected_boarding": 9,
                    "expected_exiting": 3,
                    "confidence": "94%",
                    "source": "Historical IR Patterns + Commuter Card Swipes"
                }
            },
            {
                "bus_number": "AP 16 5678",
                "bus_name": "Krishnaveni Luxury",
                "service_type": "Super Luxury",
                "capacity": 50,
                "source": "Vijayawada",
                "destination": "Guntur",
                "departure_time": "10:45 AM",
                "expected_arrival_time": "12:00 PM",
                "current_latitude": 16.4812,
                "current_longitude": 80.6053,
                "current_location_name": "Tadepalli Flyover",
                "speed": 48.0,
                "current_stop_index": 1,
                "in_count": 46,
                "out_count": 6,
                "device_id": "ESP32_BUS_002",
                "prediction": {
                    "next_stop": "Enikepadu Junction",
                    "expected_boarding": 7,
                    "expected_exiting": 3,
                    "confidence": "88%",
                    "source": "Historical IR Sensor Averages"
                }
            },
            {
                "bus_number": "AP 16 9012",
                "bus_name": "Capital Metro City",
                "service_type": "City Express",
                "capacity": 50,
                "source": "Vijayawada",
                "destination": "Guntur",
                "departure_time": "11:00 AM",
                "expected_arrival_time": "12:20 PM",
                "current_latitude": 16.4357,
                "current_longitude": 80.5645,
                "current_location_name": "Mangalagiri Bus Shelter",
                "speed": 35.0,
                "current_stop_index": 3,
                "in_count": 68,
                "out_count": 13,
                "device_id": "ESP32_BUS_003",
                "prediction": {
                    "next_stop": "Tadepalli Highway",
                    "expected_boarding": 4,
                    "expected_exiting": 7,
                    "confidence": "91%",
                    "source": "Real-time Alighting Sensor History"
                }
            },
            {
                "bus_number": "AP 16 3456",
                "bus_name": "Kanakadurga Deluxe",
                "service_type": "Metro Deluxe",
                "capacity": 50,
                "source": "Vijayawada",
                "destination": "Guntur",
                "departure_time": "11:15 AM",
                "expected_arrival_time": "12:35 PM",
                "current_latitude": 16.5062,
                "current_longitude": 80.6480,
                "current_location_name": "Vijayawada PNBS Platform 4",
                "speed": 0.0,
                "current_stop_index": 0,
                "in_count": 51,
                "out_count": 9,
                "device_id": "ESP32_BUS_004",
                "prediction": {
                    "next_stop": "Enikepadu Junction",
                    "expected_boarding": 8,
                    "expected_exiting": 4,
                    "confidence": "86%",
                    "source": "Sensor Trend Matrix"
                }
            }
        ]

        for b_data in buses_to_seed:
            bus = Bus(
                bus_number=b_data["bus_number"],
                bus_name=b_data["bus_name"],
                service_type=b_data["service_type"],
                capacity=b_data["capacity"],
                source=b_data["source"],
                destination=b_data["destination"],
                departure_time=b_data["departure_time"],
                expected_arrival_time=b_data["expected_arrival_time"],
                route_id=route_id,
                current_latitude=b_data["current_latitude"],
                current_longitude=b_data["current_longitude"],
                current_location_name=b_data["current_location_name"],
                speed=b_data["speed"],
                current_stop_index=b_data["current_stop_index"],
                status="ACTIVE"
            )
            db.add(bus)
            db.flush()

            # Seed Passenger Count
            metrics = calculate_occupancy_metrics(bus.capacity, b_data["in_count"], b_data["out_count"])
            p_count = PassengerCount(
                bus_id=bus.id,
                in_count=b_data["in_count"],
                out_count=b_data["out_count"],
                current_passengers=metrics["current_passengers"],
                available_seats=metrics["available_seats"],
                occupancy_percentage=metrics["occupancy_percentage"],
                source_type="ESP32_IR",
                event_id=f"seed-init-{bus.id}"
            )
            db.add(p_count)

            # Seed Location
            loc = BusLocation(
                bus_id=bus.id,
                latitude=b_data["current_latitude"],
                longitude=b_data["current_longitude"],
                speed=b_data["speed"],
                source_type="SIMULATED"
            )
            db.add(loc)

            # Seed Sensor Status
            s_status = SensorStatus(
                bus_id=bus.id,
                esp32_device_id=b_data["device_id"],
                sensor_status="CONNECTED",
                last_received_at=datetime.utcnow()
            )
            db.add(s_status)

            # Seed Sample IR Sensor Event Pulses
            ir_event_in = IRSensorEvent(
                bus_id=bus.id,
                device_id=b_data["device_id"],
                event_id=f"ir-in-init-{bus.id}",
                direction="IN",
                delta_count=b_data["in_count"],
                recorded_at=datetime.utcnow(),
                raw_payload=json.dumps({"beam": "front_door", "type": "PASSENGER_BOARDED", "count": b_data["in_count"]})
            )
            db.add(ir_event_in)

            if b_data["out_count"] > 0:
                ir_event_out = IRSensorEvent(
                    bus_id=bus.id,
                    device_id=b_data["device_id"],
                    event_id=f"ir-out-init-{bus.id}",
                    direction="OUT",
                    delta_count=b_data["out_count"],
                    recorded_at=datetime.utcnow(),
                    raw_payload=json.dumps({"beam": "rear_door", "type": "PASSENGER_ALIGHTED", "count": b_data["out_count"]})
                )
                db.add(ir_event_out)

            # Seed Prediction
            pred_conf = b_data["prediction"]
            pred_onboard = metrics["current_passengers"] + pred_conf["expected_boarding"] - pred_conf["expected_exiting"]
            pred_seats = max(0, bus.capacity - pred_onboard)
            pred_occ = round((pred_onboard / bus.capacity) * 100.0, 1)
            pred_level = "LOW" if pred_occ <= 40 else "MODERATE" if pred_occ <= 75 else "HIGH" if pred_occ <= 100 else "OVERCROWDED"

            prediction = CrowdPrediction(
                bus_id=bus.id,
                next_stop_name=pred_conf["next_stop"],
                current_occupancy=metrics["occupancy_percentage"],
                predicted_occupancy=pred_occ,
                expected_boarding=pred_conf["expected_boarding"],
                expected_exiting=pred_conf["expected_exiting"],
                predicted_available_seats=pred_seats,
                predicted_crowd_level=pred_level,
                confidence=pred_conf["confidence"],
                prediction_source=pred_conf["source"]
            )
            db.add(prediction)

            # Seed sample ETM tickets
            ticket = ETMTicket(
                bus_id=bus.id,
                boarding_stop_id=1,
                destination_stop_id=4,
                passenger_count=3,
                ticket_reference=f"ETM-{bus.id}-001",
                fare_amount=90.0
            )
            db.add(ticket)

        db.commit()

    # 4. Seed IR Sensor Events if none exist but buses are present
    if db.query(IRSensorEvent).count() == 0:
        all_buses = db.query(Bus).all()
        for b in all_buses:
            latest_pc = db.query(PassengerCount).filter(PassengerCount.bus_id == b.id).first()
            in_c = latest_pc.in_count if latest_pc else 30
            out_c = latest_pc.out_count if latest_pc else 5
            evt_in = IRSensorEvent(
                bus_id=b.id,
                device_id=f"ESP32_BUS_{b.id:03d}",
                event_id=f"ir-in-init-{b.id}",
                direction="IN",
                delta_count=in_c,
                recorded_at=datetime.utcnow(),
                raw_payload=json.dumps({"beam": "front_door", "type": "PASSENGER_BOARDED", "count": in_c})
            )
            db.add(evt_in)
            if out_c > 0:
                evt_out = IRSensorEvent(
                    bus_id=b.id,
                    device_id=f"ESP32_BUS_{b.id:03d}",
                    event_id=f"ir-out-init-{b.id}",
                    direction="OUT",
                    delta_count=out_c,
                    recorded_at=datetime.utcnow(),
                    raw_payload=json.dumps({"beam": "rear_door", "type": "PASSENGER_ALIGHTED", "count": out_c})
                )
                db.add(evt_out)
        db.commit()

def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_demo_data(db)
    finally:
        db.close()
