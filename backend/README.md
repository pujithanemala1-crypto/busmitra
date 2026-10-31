# BusMitra Backend – Smart Public Transportation, Live Bus Tracking & IR Sensor Crowd Monitoring System

**Tagline:** *Your Travel Buddy, Always!*

---

## 1. Overview & Architecture

BusMitra Backend is a high-performance Python FastAPI service providing real-time transit telematics, bi-directional infrared (IR) passenger counting, dynamic crowd density classification, Next-Stop crowd forecasting, Conductor ETM (Electronic Ticketing Machine) synchronization, and WebSocket live updates for Indian state public transport networks.

```
BusMitra Architecture:

  [ESP32 Bi-Directional IR Sensors] ─── POST /api/sensors/ir-data ───┐
  [Conductor ETM Ticketing Machine] ─── POST /api/etm/tickets ───────┤
  [Driver Smartphone / GPS Module] ──── POST /api/buses/{id}/location ───┤
                                                                      │
                                                           ┌──────────▼──────────┐
                                                           │   BusMitra FastAPI   │
                                                           │   Backend Server    │
                                                           │   (Python 3.11+)    │
                                                           └──────────┬──────────┘
                                                                      │
                              ┌───────────────────────────────────────┼────────────────────────────────────────┐
                              ▼                                       ▼                                        ▼
                     [SQLite Database]                      [WebSocket Manager]                       [Prediction Engine]
                  (SQLAlchemy Models & ORM)                  /ws/buses/{busId}                      (Historical + ETM Stats)
                              ▲                                       │                                        ▲
                              └───────────────────────────────────────┴────────────────────────────────────────┘
                                                                      ▲
                                                          [BusMitra Web Frontend]
                                                          (Live Leaflet Map & Lab)
```

---

## 2. Technology Stack

- **Python:** 3.11+
- **Framework:** FastAPI
- **ASGI Server:** Uvicorn
- **Database:** SQLite (with SQLAlchemy ORM)
- **Data Validation:** Pydantic v2
- **Real-Time Streaming:** WebSockets
- **Authentication:** JWT (JSON Web Tokens) with Passlib Bcrypt
- **Testing:** Pytest & FastAPI TestClient

---

## 3. Directory Structure

```
backend/
├── app/
│   ├── config.py             # Environment configurations and thresholds
│   ├── database.py           # SQLite connection and automatic demo data seeding
│   ├── main.py               # FastAPI entry point, CORS, lifespan & WebSocket endpoint
│   ├── models.py             # SQLAlchemy database models
│   ├── schemas.py            # Pydantic request and response models
│   ├── routers/
│   │   ├── health.py         # GET /api/health prober
│   │   ├── buses.py          # GET /api/buses, search, route, timings, CRUD
│   │   ├── routes.py         # GET /api/routes, stops geometry
│   │   ├── stops.py          # GET /api/stops
│   │   ├── tracking.py       # POST/GET /api/buses/{id}/location, ETA, history
│   │   ├── occupancy.py      # GET/POST /api/buses/{id}/occupancy, passenger counts
│   │   ├── sensors.py        # POST /api/sensors/ir-data, GET /api/sensors/status/{id}
│   │   ├── prediction.py     # GET /api/buses/{id}/crowd-prediction
│   │   └── users.py          # Admin JWT auth & Conductor ETM ticket endpoints
│   ├── services/
│   │   ├── bus_service.py    # Bus data assembly & lookup logic
│   │   ├── gps_service.py    # Location ingestion & history tracking
│   │   ├── sensor_service.py # Bi-directional IR counting & deduplication
│   │   ├── crowd_service.py  # Centralized occupancy calculations
│   │   ├── prediction_service.py # Next-stop crowd forecasting engine
│   │   └── eta_service.py    # Dynamic ETA and delay calculations
│   ├── utils/
│   │   └── calculations.py   # Occupancy formulas, crowd thresholds & Haversine math
│   └── websocket/
│       └── manager.py        # Real-time WebSocket connection manager
├── data/
│   └── busmitra.db           # SQLite database file
├── tests/
│   └── test_api.py           # Comprehensive pytest suite
├── requirements.txt          # Python package dependencies
├── .env.example              # Environment variables template
└── README.md                 # Complete documentation
```

---

## 4. Database Schema & Architecture

The database is built on SQLite using SQLAlchemy ORM with foreign keys and WAL (Write-Ahead Logging) mode:
- **Database File:** `backend/data/busmitra.db`
- **ACID & Concurrency:** Configured with `PRAGMA foreign_keys=ON;` and `PRAGMA journal_mode=WAL;`
- **Persistence:** Tables are auto-created at startup; all records persist across server restarts.
- **Idempotency:** Initial demo data seeding runs idempotently without duplicating existing rows.

### Registered SQLAlchemy Models & Tables (10 Tables):
1. **`users`**: Administrative accounts with PBKDF2-SHA256 hashed credentials. Default: `admin` / `admin123`.
2. **`buses`**: APSRTC fleet records (e.g. `AP 16 1234`, `AP 16 5678`, `AP 16 9012`), service type, capacity, current coordinates, speed, and status.
3. **`routes`**: Transit corridors (`Vijayawada to Guntur`, `Vijayawada to Mangalagiri`, `Vijayawada to Gannavaram`), distances, and waypoint coordinates.
4. **`stops`**: Ordered transit stops along each corridor with latitude/longitude and scheduled arrival times.
5. **`bus_locations`**: Historical GPS log records with speed, coordinates, and timestamp.
6. **`passenger_counts`**: Bi-directional entry (`in_count`) and exit (`out_count`) logs with unique `event_id` to prevent duplicate processing.
7. **`ir_sensor_events`**: Hardware bi-directional IR pulse log records (`IN` and `OUT`) with device IDs and raw JSON telemetry payloads.
8. **`sensor_status`**: Connection heartbeats, device IDs, and timeout detection for ESP32 microcontrollers.
9. **`crowd_predictions`**: Forecasted occupancy, expected boarding, and alighting for upcoming stations.
10. **`etm_tickets`**: Ticketing logs from bus conductors indicating boarding and destination stops.

---

## 5. Core REST API Endpoints

### Bus Management
- `GET /api/buses` – List all available buses with real-time seat availability and crowd levels.
- `GET /api/buses/search?source=Vijayawada&destination=Guntur` – Search matching route corridors.
- `GET /api/buses/{busId}` – Return complete bus telemetry and status.
- `GET /api/buses/{busId}/route` – Return route waypoints and ordered intermediate stops.
- `GET /api/buses/{busId}/timings` – Scheduled departure, expected arrival, delay, and current status.
- `POST /api/buses` – Add a new bus (Admin token required).
- `PUT /api/buses/{busId}` – Update bus information (Admin token required).

### GPS Live Tracking
- `POST /api/buses/{busId}/location` – Save live GPS coordinates and broadcast `BUS_LOCATION_UPDATED` via WebSocket.
- `GET /api/buses/{busId}/location` – Current latitude, longitude, speed, and GPS status.
- `GET /api/buses/{busId}/location/history` – Recent GPS breadcrumbs.
- `GET /api/buses/{busId}/eta` – Distance to next stop, estimated arrival minutes, and delay.

### IR Passenger Counting & Occupancy
- `GET /api/buses/{busId}/occupancy` – Return current passengers, available seats, occupancy percentage, and crowd tier (`LOW`, `MODERATE`, `HIGH`, `OVERCROWDED`).
- `POST /api/buses/{busId}/passenger-count` – Ingest passenger events (incremental or cumulative).

### ESP32 Direct Sensor Protocol
- `POST /api/sensors/ir-data` – Ingest direct hardware pulses from ESP32 into `ir_sensor_events`.
  ```json
  {
    "device_id": "ESP32_BUS_001",
    "bus_id": 1,
    "event_id": "pulse-20261031-0012",
    "direction": "IN",
    "recorded_at": "2026-10-31T10:30:00"
  }
  ```
- `GET /api/sensors/status/{busId}` – Device connection status, timeout detector, and total pulse counts.

### Crowd Prediction & ETM Integration
- `GET /api/buses/{busId}/crowd-prediction` – Next-stop predicted occupancy, expected boarding, and alighting.
- `POST /api/etm/tickets` – Log electronic ticket sales.
- `GET /api/buses/{busId}/expected-exits` – Predict upcoming stop alighting from ETM tickets and flag mismatches with IR sensors.

### Database & System Health
- `GET /api/health` – Returns backend health, database connection state, and active bus counts.
- `GET /api/health/db` – Deep database diagnostics: verifies SQLite file status, latency, PRAGMA foreign keys, WAL mode, and table list.
- `GET /api/admin/database-summary` – Administrator endpoint returning live record counts for all 10 tables and SQLite file statistics.

---

## 6. Real-Time WebSockets

Connect to:
```
ws://127.0.0.1:8000/ws/buses/{busId}
```

Connected clients receive live JSON broadcasts when telematics change:
- `BUS_LOCATION_UPDATED`: Real-time GPS coordinates and speed.
- `OCCUPANCY_UPDATED`: Real-time passenger counts, available seats, and occupancy percentage.
- `CROWD_LEVEL_UPDATED`: Dynamic crowd tier transitions.
- `SENSOR_STATUS_UPDATED`: ESP32 heartbeat and connectivity.
- `ETA_UPDATED`: Approaching stop travel times.
- `CROWD_PREDICTION_UPDATED`: Forecast adjustments.

---

## 7. Windows Command Prompt (CMD) Execution Instructions

Follow these exact steps to run the backend on Windows:

### Step 1: Open Windows Command Prompt
Open `cmd.exe` and navigate to the backend folder:
```cmd
cd path\to\BusMitra\backend
```

### Step 2: Create a Virtual Environment
```cmd
python -m venv venv
```

### Step 3: Activate the Virtual Environment
```cmd
venv\Scripts\activate
```

### Step 4: Install Dependencies
```cmd
pip install -r requirements.txt
```

### Step 5: (Optional) Standalone Database Verification Script
To inspect table counts or manually initialize:
```cmd
python scripts\init_db.py
```

### Step 6: Start the FastAPI Server
```cmd
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### Step 7: Verify and Explore
- Open Swagger Documentation: **http://127.0.0.1:8000/docs**
- Open ReDoc Documentation: **http://127.0.0.1:8000/redoc**
- System Health: **http://127.0.0.1:8000/api/health**
- Database Health & Pragmas: **http://127.0.0.1:8000/api/health/db**
- Default Admin Login: `admin` / `admin123`
- Admin Database Summary: `GET /api/admin/database-summary` (with Admin Bearer token)
