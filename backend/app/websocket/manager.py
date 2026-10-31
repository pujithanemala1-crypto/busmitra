"""
BUSMITRA - WebSocket Connection Manager
Maintains active connections per bus ID and broadcasts real-time telematics
events (Location, Occupancy, Crowd Level, Sensors, ETA, Predictions).
"""
import json
import logging
from typing import Dict, List, Any
from fastapi import WebSocket

logger = logging.getLogger("busmitra.websocket")

class ConnectionManager:
    def __init__(self):
        # Maps bus_id (as string) to list of active WebSockets
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, bus_id: str):
        await websocket.accept()
        key = str(bus_id).strip()
        if key not in self.active_connections:
            self.active_connections[key] = []
        self.active_connections[key].append(websocket)
        logger.info(f"WebSocket client connected to bus_id={key}. Total on bus: {len(self.active_connections[key])}")

    def disconnect(self, websocket: WebSocket, bus_id: str):
        key = str(bus_id).strip()
        if key in self.active_connections:
            if websocket in self.active_connections[key]:
                self.active_connections[key].remove(websocket)
            if len(self.active_connections[key]) == 0:
                del self.active_connections[key]
        logger.info(f"WebSocket client disconnected from bus_id={key}")

    async def broadcast_to_bus(self, bus_id: str, event_type: str, data: Any):
        """
        Broadcasts message to all clients subscribed to a particular bus.
        Event types:
        - BUS_LOCATION_UPDATED
        - OCCUPANCY_UPDATED
        - CROWD_LEVEL_UPDATED
        - SENSOR_STATUS_UPDATED
        - ETA_UPDATED
        - CROWD_PREDICTION_UPDATED
        """
        key = str(bus_id).strip()
        if key not in self.active_connections:
            return

        payload = {
            "event": event_type,
            "bus_id": key,
            "data": data
        }

        dead_connections = []
        for connection in self.active_connections[key]:
            try:
                await connection.send_text(json.dumps(payload, default=str))
            except Exception as e:
                logger.warning(f"Error sending WS message to client on bus {key}: {e}")
                dead_connections.append(connection)

        # Cleanup dropped sockets
        for dead in dead_connections:
            self.disconnect(dead, key)

    async def broadcast_all(self, event_type: str, data: Any):
        """Broadcasts system-wide notification to all connected clients."""
        payload = {
            "event": event_type,
            "data": data
        }
        for key in list(self.active_connections.keys()):
            for conn in list(self.active_connections[key]):
                try:
                    await conn.send_text(json.dumps(payload, default=str))
                except Exception:
                    self.disconnect(conn, key)

ws_manager = ConnectionManager()
