"""
BUSMITRA - Main FastAPI Application
Smart Public Transportation, Live Bus Tracking & IR Sensor-Based Crowd Monitoring System.
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db
from app.routers import (
    health, buses, routes, stops, tracking,
    occupancy, sensors, prediction, users
)
from app.websocket.manager import ws_manager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("busmitra.main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize Database & Seed Demo Data
    logger.info("Initializing BusMitra database and verification seeds...")
    init_db()
    logger.info("BusMitra backend initialized successfully.")
    yield
    # Shutdown
    logger.info("BusMitra backend shutting down.")

app = FastAPI(
    title=f"{settings.PROJECT_NAME} Transit API",
    description="Backend for BusMitra: Smart Public Transportation, Live Bus Tracking & IR Sensor-Based Crowd Monitoring System",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS Middleware (Fully open for frontend integration across any port/domain)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Modular Routers
app.include_router(health.router)
app.include_router(buses.router)
app.include_router(routes.router)
app.include_router(stops.router)
app.include_router(tracking.router)
app.include_router(occupancy.router)
app.include_router(sensors.router)
app.include_router(prediction.router)
app.include_router(users.router)

# WebSocket Endpoint for Live Telematics
@app.websocket("/ws/buses/{bus_id}")
async def websocket_bus_endpoint(websocket: WebSocket, bus_id: str):
    await ws_manager.connect(websocket, bus_id)
    try:
        while True:
            # Keep socket alive and receive client pings/messages
            data = await websocket.receive_text()
            # Echo heartbeat or client request
            await websocket.send_text('{"event": "PONG", "status": "connected"}')
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, bus_id)
    except Exception as e:
        logger.warning(f"WebSocket error on bus {bus_id}: {e}")
        ws_manager.disconnect(websocket, bus_id)

@app.get("/")
def root_endpoint():
    return {
        "project": "BusMitra",
        "tagline": "Your Travel Buddy, Always!",
        "system": "Smart Public Transportation & IR Sensor Crowd Monitoring",
        "docs": "/docs",
        "health": "/api/health",
        "demo_buses": ["AP 16 1234", "AP 16 5678", "AP 16 9012"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
