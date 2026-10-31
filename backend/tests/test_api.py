"""
BUSMITRA - Backend Test Suite
Comprehensive automated tests covering Database, Buses, GPS tracking,
IR sensor counting, Occupancy calculations, Predictions, Duplicate handling, and ETM tickets.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import init_db

client = TestClient(app)

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    init_db()

def test_health_check():
    """Verify backend health and database connectivity."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["HEALTHY", "DEGRADED"]
    assert data["database_connected"] is True
    assert data["active_buses"] >= 3

def test_get_all_buses():
    """Verify bus catalog returns seeded demonstration buses."""
    response = client.get("/api/buses")
    assert response.status_code == 200
    buses = response.json()
    assert len(buses) >= 3
    numbers = [b["number"] for b in buses]
    assert "AP 16 1234" in numbers
    assert "AP 16 5678" in numbers
    assert "AP 16 9012" in numbers

def test_bus_search_and_filter():
    """Verify searching by corridor."""
    response = client.get("/api/buses/search?source=Vijayawada&destination=Guntur")
    assert response.status_code == 200
    results = response.json()
    assert len(results) >= 1
    assert any(b["destination"] == "Guntur" for b in results)

def test_bus_details_and_route():
    """Verify single bus details and route stops."""
    response = client.get("/api/buses/AP161234")
    assert response.status_code == 200
    bus = response.json()
    assert bus["number"] == "AP 16 1234"
    assert bus["capacity"] == 50

    # Route stops
    route_resp = client.get("/api/buses/AP161234/route")
    assert route_resp.status_code == 200
    route_data = route_resp.json()
    assert len(route_data["stops"]) >= 4
    stop_names = [s["name"] for s in route_data["stops"]]
    assert any("Vijayawada" in s for s in stop_names)
    assert any("Guntur" in s for s in stop_names)

def test_gps_location_update():
    """Verify GPS coordinate ingestion and retrieval."""
    payload = {
        "latitude": 16.4850,
        "longitude": 80.6120,
        "speed": 55.4,
        "location_name": "Tadepalli Highway Test",
        "source_type": "GPS_DRIVER"
    }
    post_res = client.post("/api/buses/AP161234/location", json=payload)
    assert post_res.status_code == 200
    assert post_res.json()["success"] is True

    get_res = client.get("/api/buses/AP161234/location")
    assert get_res.status_code == 200
    loc_data = get_res.json()
    assert loc_data["latitude"] == 16.4850
    assert loc_data["speed"] == 55.4

def test_passenger_ir_sensor_in_and_out():
    """Verify passenger boarding (+1 IN) and alighting (-1 OUT)."""
    # 1. Check initial occupancy
    init_res = client.get("/api/buses/AP161234/occupancy")
    assert init_res.status_code == 200
    initial_passengers = init_res.json()["current_passengers"]
    initial_in = init_res.json()["total_in"]

    # 2. Board passenger via IN event
    board_res = client.post("/api/buses/AP161234/passenger-count", json={"eventType": "IN"})
    assert board_res.status_code == 200
    new_in = board_res.json()["metrics"]["total_in"]
    new_passengers = board_res.json()["metrics"]["current_passengers"]
    assert new_in == initial_in + 1
    assert new_passengers == initial_passengers + 1

    # 3. Alight passenger via OUT event
    alight_res = client.post("/api/buses/AP161234/passenger-count", json={"eventType": "OUT"})
    assert alight_res.status_code == 200
    final_passengers = alight_res.json()["metrics"]["current_passengers"]
    assert final_passengers == new_passengers - 1

def test_occupancy_and_available_seats_calculation():
    """Verify dynamic seat formulas and crowd thresholds."""
    occ_res = client.get("/api/buses/AP161234/occupancy")
    assert occ_res.status_code == 200
    data = occ_res.json()
    capacity = data["capacity"]
    passengers = data["current_passengers"]
    available_seats = data["available_seats"]
    expected_seats = max(0, capacity - passengers)
    assert available_seats == expected_seats
    assert data["crowd_level"] in ["LOW", "MODERATE", "HIGH", "OVERCROWDED"]

def test_esp32_direct_sensor_and_idempotency():
    """Verify ESP32 hardware endpoint and duplicate event suppression."""
    unique_event_id = "test-event-uuid-8942-001"
    event_payload = {
        "device_id": "ESP32_BUS_001",
        "bus_id": 1,
        "event_id": unique_event_id,
        "direction": "IN"
    }

    # First event submission
    res1 = client.post("/api/sensors/ir-data", json=event_payload)
    assert res1.status_code == 200
    count1 = res1.json()["current_passengers"]

    # Duplicate event submission with identical event_id
    res2 = client.post("/api/sensors/ir-data", json=event_payload)
    assert res2.status_code == 200
    count2 = res2.json()["current_passengers"]

    # Duplicate must not increment passenger count again
    assert count1 == count2

def test_invalid_sensor_event_prevent_negative_passengers():
    """Verify that OUT count cannot exceed current onboard passengers."""
    # Attempting to disembark 999 passengers from bus with ~25 passengers
    payload = {
        "out_count": 999,
        "in_count": 0
    }
    res = client.post("/api/buses/AP161234/passenger-count", json=payload)
    assert res.status_code == 400
    assert "cannot be negative" in res.json()["detail"].lower()

def test_crowd_prediction():
    """Verify next-stop crowd prediction forecast."""
    res = client.get("/api/buses/AP161234/crowd-prediction")
    assert res.status_code == 200
    data = res.json()
    assert "next_stop" in data
    assert "predicted_occupancy" in data
    assert "expected_boarding" in data
    assert "prediction_confidence" in data
    assert data["is_simulated"] is True

def test_etm_ticket_insertion_and_expected_exits():
    """Verify ETM ticket logging and expected exits calculation."""
    ticket_payload = {
        "bus_id": 1,
        "boarding_stop_id": 1,
        "destination_stop_id": 4, # Mangalagiri
        "passenger_count": 2,
        "ticket_reference": "TEST-ETM-TICKET-0099",
        "fare_amount": 60.0
    }
    t_res = client.post("/api/etm/tickets", json=ticket_payload)
    assert t_res.status_code == 200
    assert t_res.json()["ticket_reference"] == "TEST-ETM-TICKET-0099"

    # Query expected exits
    exit_res = client.get("/api/buses/1/expected-exits")
    assert exit_res.status_code == 200
    assert "expected_exits_etm" in exit_res.json()

def test_eta_service():
    """Verify ETA calculation."""
    eta_res = client.get("/api/buses/AP161234/eta")
    assert eta_res.status_code == 200
    data = eta_res.json()
    assert "estimated_arrival" in data
    assert "distance_to_next_stop_km" in data

def test_websocket_connection():
    """Verify WebSocket connection and ping/pong."""
    with client.websocket_connect("/ws/buses/1") as ws:
        ws.send_text("PING")
        reply = ws.receive_text()
        assert "PONG" in reply

def test_database_health_endpoint():
    """Verify GET /api/health/db returns full SQLite diagnostics."""
    res = client.get("/api/health/db")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "CONNECTED"
    assert data["database_engine"] == "SQLite"
    assert data["database_file_exists"] is True
    assert data["database_size_bytes"] > 0
    assert data["foreign_keys_enabled"] is True
    assert "WAL" in data["journal_mode"]
    assert data["table_count"] >= 10
    expected_tables = [
        "users", "buses", "routes", "stops", "bus_locations",
        "passenger_counts", "ir_sensor_events", "sensor_status",
        "crowd_predictions", "etm_tickets"
    ]
    for tbl in expected_tables:
        assert tbl in data["tables"], f"Table '{tbl}' missing from SQLite database"

def test_admin_database_summary_endpoint():
    """Verify admin login and GET /api/admin/database-summary access."""
    # 1. Login with demo admin credentials
    login_res = client.post("/api/users/login", json={"username": "admin", "password": "admin123"})
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    assert token is not None

    # 2. Query admin database summary
    headers = {"Authorization": f"Bearer {token}"}
    sum_res = client.get("/api/admin/database-summary", headers=headers)
    assert sum_res.status_code == 200
    data = sum_res.json()
    assert data["status"] == "SUCCESS"
    assert data["requested_by"] == "admin"
    assert data["database_exists"] is True
    assert data["total_records"] >= 40
    counts = data["table_counts"]
    assert counts["users"] >= 1
    assert counts["buses"] >= 3
    assert counts["routes"] >= 3
    assert counts["stops"] >= 6
    assert counts["passenger_counts"] >= 3
    assert counts["ir_sensor_events"] >= 3

def test_unauthorized_admin_summary_access():
    """Verify GET /api/admin/database-summary rejects unauthenticated requests."""
    res = client.get("/api/admin/database-summary")
    assert res.status_code == 401
