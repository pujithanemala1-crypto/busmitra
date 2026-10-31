"""
BUSMITRA - Pydantic Schemas & Validation Models
Covers all Request/Response models for Buses, Routes, Stops, Telematics,
Sensors, Occupancy, Predictions, ETM and Admin Users.
"""
from datetime import datetime
from typing import List, Optional, Any
from pydantic import BaseModel, Field, ConfigDict

# --- Health Schema ---
class HealthResponse(BaseModel):
    status: str
    database_connected: bool
    active_buses: int
    demo_mode: bool
    timestamp: datetime

# --- Bus Schemas ---
class BusBase(BaseModel):
    bus_number: str = Field(..., json_schema_extra={"example": "AP 16 1234"})
    bus_name: str = Field(..., json_schema_extra={"example": "Amaravati Express"})
    service_type: str = Field(default="Express", json_schema_extra={"example": "Express"})
    capacity: int = Field(default=50, ge=1, le=120)
    source: str = Field(..., json_schema_extra={"example": "Vijayawada"})
    destination: str = Field(..., json_schema_extra={"example": "Guntur"})
    departure_time: str = Field(default="10:30 AM")
    expected_arrival_time: str = Field(default="11:45 AM")
    route_id: Optional[int] = None
    status: str = Field(default="ACTIVE")

class BusCreate(BusBase):
    pass

class BusUpdate(BaseModel):
    bus_name: Optional[str] = None
    service_type: Optional[str] = None
    capacity: Optional[int] = None
    departure_time: Optional[str] = None
    expected_arrival_time: Optional[str] = None
    route_id: Optional[int] = None
    status: Optional[str] = None

class BusResponse(BusBase):
    id: int
    current_latitude: Optional[float] = None
    current_longitude: Optional[float] = None
    current_location_name: Optional[str] = None
    speed: float = 0.0
    current_stop_index: int = 0
    current_passengers: int = 0
    available_seats: int = 50
    occupancy_percent: float = 0.0
    crowd_level: str = "LOW"
    sensor_in_count: int = 0
    sensor_out_count: int = 0
    gps_status: str = "ACTIVE"
    last_updated: Optional[str] = "Just now"
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

# --- Route & Stops Schemas ---
class StopBase(BaseModel):
    stop_name: str = Field(..., json_schema_extra={"example": "Vijayawada (PNBS)"})
    stop_order: int = Field(..., ge=1)
    latitude: float
    longitude: float
    scheduled_arrival_time: Optional[str] = "10:30 AM"

class StopCreate(StopBase):
    route_id: int

class StopResponse(StopBase):
    id: int
    route_id: int

    model_config = ConfigDict(from_attributes=True)

class RouteBase(BaseModel):
    route_name: str = Field(..., json_schema_extra={"example": "Vijayawada to Guntur Express Corridor"})
    source: str = Field(..., json_schema_extra={"example": "Vijayawada"})
    destination: str = Field(..., json_schema_extra={"example": "Guntur"})
    total_distance: float = Field(default=34.5)
    estimated_duration: int = Field(default=75) # in minutes

class RouteCreate(RouteBase):
    waypoints_json: Optional[str] = None

class RouteResponse(RouteBase):
    id: int
    waypoints: Optional[List[List[float]]] = None
    stops: List[StopResponse] = []
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# --- Location & GPS Tracking Schemas ---
class LocationCreate(BaseModel):
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    speed: float = Field(default=0.0, ge=0.0)
    location_name: Optional[str] = None
    recorded_at: Optional[datetime] = None
    source_type: str = Field(default="SIMULATED", json_schema_extra={"example": "SIMULATED"})

class LocationResponse(BaseModel):
    bus_id: Any
    bus_number: Optional[str] = None
    latitude: float
    longitude: float
    current_location_name: Optional[str] = None
    speed_kmh: float
    recorded_at: datetime
    gps_status: str
    source_type: str
    is_simulated: bool

# --- Passenger & IR Sensor Counts ---
class PassengerCountCreate(BaseModel):
    in_count: Optional[int] = Field(default=0, ge=0)
    out_count: Optional[int] = Field(default=0, ge=0)
    event_type: Optional[str] = None # "IN", "OUT", or "CUMULATIVE"
    is_cumulative: bool = Field(default=False)
    event_id: Optional[str] = None
    device_id: Optional[str] = "ESP32_DEFAULT"
    source_type: str = Field(default="ESP32_IR")
    recorded_at: Optional[datetime] = None

class OccupancyResponse(BaseModel):
    bus_id: Any
    bus_number: Optional[str] = None
    capacity: int
    total_in: int
    total_out: int
    current_passengers: int
    available_seats: int
    occupancy_percentage: float
    crowd_level: str
    sensor_status: str
    last_updated: str
    data_source: str
    is_simulated: bool

# --- ESP32 Direct Sensor Protocol ---
class IRSensorEvent(BaseModel):
    device_id: str = Field(..., json_schema_extra={"example": "ESP32_BUS_001"})
    bus_id: Any = Field(..., json_schema_extra={"example": 1})
    event_id: str = Field(..., json_schema_extra={"example": "event-unique-001"})
    direction: str = Field(..., pattern="^(IN|OUT)$", json_schema_extra={"example": "IN"})
    recorded_at: Optional[datetime] = None

class SensorStatusResponse(BaseModel):
    bus_id: Any
    esp32_device_id: str
    connection_status: str
    last_received_at: Optional[datetime]
    total_in: int
    total_out: int
    is_simulated: bool

# --- Crowd Prediction Schemas ---
class PredictionResponse(BaseModel):
    bus_id: Any
    bus_number: Optional[str] = None
    next_stop: Optional[str] = None
    current_occupancy: str
    predicted_occupancy: float
    predicted_occupancy_formatted: str
    expected_boarding: int
    expected_exiting: int
    predicted_available_seats: int
    predicted_crowd_level: str
    prediction_confidence: str
    prediction_source: str
    is_simulated: bool
    generated_at: datetime

# --- ETM (Electronic Ticketing Machine) ---
class ETMTicketCreate(BaseModel):
    bus_id: Any
    boarding_stop_id: Optional[int] = None
    destination_stop_id: Optional[int] = None
    passenger_count: int = Field(default=1, ge=1)
    ticket_reference: str = Field(..., json_schema_extra={"example": "ETM-VJA-GNT-10928"})
    fare_amount: float = Field(default=45.0)

class ETMTicketResponse(BaseModel):
    id: int
    bus_id: int
    boarding_stop_id: Optional[int]
    destination_stop_id: Optional[int]
    passenger_count: int
    ticket_reference: str
    fare_amount: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ExpectedExitsResponse(BaseModel):
    bus_id: Any
    upcoming_stop_id: Optional[int]
    upcoming_stop_name: Optional[str]
    expected_exits_etm: int
    actual_ir_out_count: int
    mismatch_detected: bool
    notes: str

# --- ETA & Timings ---
class ETAResponse(BaseModel):
    bus_id: Any
    bus_number: Optional[str]
    current_location: Optional[str]
    next_stop: Optional[str]
    distance_to_next_stop_km: float
    estimated_arrival: str
    delay_minutes: int
    status: str
    data_source: str

# --- User & JWT Authentication ---
class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str
    role: Optional[str] = "admin"

class UserLogin(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    username: str

class UserResponse(UserBase):
    id: int
    role: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
