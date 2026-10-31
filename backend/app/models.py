"""
BUSMITRA - SQLAlchemy Database Models
Includes Buses, Routes, Stops, GPS Bus Locations, Passenger Counts, Sensor Status,
Crowd Predictions, ETM Tickets, and Administrator Users.
"""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Index, Text
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Bus(Base):
    __tablename__ = "buses"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    bus_number = Column(String(32), unique=True, index=True, nullable=False) # e.g. "AP 16 1234"
    bus_name = Column(String(100), nullable=False) # e.g. "Amaravati Express"
    service_type = Column(String(50), default="Express") # Express, Super Luxury, City Express
    capacity = Column(Integer, default=50, nullable=False)
    source = Column(String(100), nullable=False)
    destination = Column(String(100), nullable=False)
    departure_time = Column(String(20), default="10:30 AM")
    expected_arrival_time = Column(String(20), default="11:45 AM")
    route_id = Column(Integer, ForeignKey("routes.id"), nullable=True, index=True)
    current_latitude = Column(Float, nullable=True)
    current_longitude = Column(Float, nullable=True)
    current_location_name = Column(String(150), nullable=True)
    speed = Column(Float, default=0.0)
    current_stop_index = Column(Integer, default=0)
    status = Column(String(30), default="ACTIVE") # ACTIVE, INACTIVE, DELAYED, MAINTENANCE
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    route = relationship("Route", back_populates="buses")
    locations = relationship("BusLocation", back_populates="bus", cascade="all, delete-orphan")
    passenger_counts = relationship("PassengerCount", back_populates="bus", cascade="all, delete-orphan")
    ir_sensor_events = relationship("IRSensorEvent", back_populates="bus", cascade="all, delete-orphan")
    sensor_statuses = relationship("SensorStatus", back_populates="bus", cascade="all, delete-orphan")
    predictions = relationship("CrowdPrediction", back_populates="bus", cascade="all, delete-orphan")
    etm_tickets = relationship("ETMTicket", back_populates="bus", cascade="all, delete-orphan")


class Route(Base):
    __tablename__ = "routes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    route_name = Column(String(150), unique=True, index=True, nullable=False)
    source = Column(String(100), nullable=False, index=True)
    destination = Column(String(100), nullable=False, index=True)
    total_distance = Column(Float, default=0.0) # in kilometers
    estimated_duration = Column(Integer, default=60) # in minutes
    waypoints_json = Column(Text, nullable=True) # JSON list of [lat, lng] coordinates
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    buses = relationship("Bus", back_populates="route")
    stops = relationship("Stop", back_populates="route", order_by="Stop.stop_order", cascade="all, delete-orphan")


class Stop(Base):
    __tablename__ = "stops"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    route_id = Column(Integer, ForeignKey("routes.id"), nullable=False, index=True)
    stop_name = Column(String(150), nullable=False, index=True)
    stop_order = Column(Integer, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    scheduled_arrival_time = Column(String(20), nullable=True)

    # Relationships
    route = relationship("Route", back_populates="stops")
    boarding_tickets = relationship("ETMTicket", foreign_keys="ETMTicket.boarding_stop_id")
    destination_tickets = relationship("ETMTicket", foreign_keys="ETMTicket.destination_stop_id")


class BusLocation(Base):
    __tablename__ = "bus_locations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    bus_id = Column(Integer, ForeignKey("buses.id"), nullable=False, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    speed = Column(Float, default=0.0) # km/h
    recorded_at = Column(DateTime, default=datetime.utcnow, index=True)
    source_type = Column(String(30), default="SIMULATED") # "SIMULATED", "GPS_DRIVER", "HARDWARE_GPS"

    bus = relationship("Bus", back_populates="locations")


class PassengerCount(Base):
    __tablename__ = "passenger_counts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    bus_id = Column(Integer, ForeignKey("buses.id"), nullable=False, index=True)
    in_count = Column(Integer, default=0, nullable=False)
    out_count = Column(Integer, default=0, nullable=False)
    current_passengers = Column(Integer, default=0, nullable=False)
    available_seats = Column(Integer, default=0, nullable=False)
    occupancy_percentage = Column(Float, default=0.0, nullable=False)
    event_id = Column(String(64), unique=True, nullable=True, index=True) # for deduplication
    recorded_at = Column(DateTime, default=datetime.utcnow, index=True)
    source_type = Column(String(30), default="SIMULATED") # "ESP32_IR", "SIMULATED", "MANUAL"

    bus = relationship("Bus", back_populates="passenger_counts")


class IRSensorEvent(Base):
    __tablename__ = "ir_sensor_events"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    bus_id = Column(Integer, ForeignKey("buses.id", ondelete="CASCADE"), nullable=False, index=True)
    device_id = Column(String(64), nullable=False, index=True)
    event_id = Column(String(64), unique=True, nullable=True, index=True) # for hardware deduplication
    direction = Column(String(10), nullable=False) # "IN" or "OUT"
    delta_count = Column(Integer, default=1, nullable=False)
    recorded_at = Column(DateTime, default=datetime.utcnow, index=True)
    raw_payload = Column(Text, nullable=True)

    bus = relationship("Bus", back_populates="ir_sensor_events")


class SensorStatus(Base):
    __tablename__ = "sensor_status"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    bus_id = Column(Integer, ForeignKey("buses.id"), nullable=False, index=True)
    esp32_device_id = Column(String(64), nullable=False, index=True)
    sensor_status = Column(String(30), default="CONNECTED") # CONNECTED, DISCONNECTED, WAITING_FOR_DATA
    last_received_at = Column(DateTime, default=datetime.utcnow, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    bus = relationship("Bus", back_populates="sensor_statuses")


class CrowdPrediction(Base):
    __tablename__ = "crowd_predictions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    bus_id = Column(Integer, ForeignKey("buses.id"), nullable=False, index=True)
    next_stop_id = Column(Integer, ForeignKey("stops.id"), nullable=True)
    next_stop_name = Column(String(150), nullable=True)
    current_occupancy = Column(Float, default=0.0)
    predicted_occupancy = Column(Float, default=0.0)
    expected_boarding = Column(Integer, default=0)
    expected_exiting = Column(Integer, default=0)
    predicted_available_seats = Column(Integer, default=0)
    predicted_crowd_level = Column(String(30), default="LOW") # LOW, MODERATE, HIGH, OVERCROWDED
    confidence = Column(String(20), default="90%")
    prediction_source = Column(String(100), default="Historical IR Sensor Averages")
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    bus = relationship("Bus", back_populates="predictions")


class ETMTicket(Base):
    __tablename__ = "etm_tickets"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    bus_id = Column(Integer, ForeignKey("buses.id"), nullable=False, index=True)
    boarding_stop_id = Column(Integer, ForeignKey("stops.id"), nullable=True)
    destination_stop_id = Column(Integer, ForeignKey("stops.id"), nullable=True)
    passenger_count = Column(Integer, default=1, nullable=False)
    ticket_reference = Column(String(64), unique=True, index=True, nullable=False)
    fare_amount = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    bus = relationship("Bus", back_populates="etm_tickets")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), default="admin") # "admin", "operator", "commuter"
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
