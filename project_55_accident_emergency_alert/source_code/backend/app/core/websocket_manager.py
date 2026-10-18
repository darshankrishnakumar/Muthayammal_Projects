"""
Real-Time WebSocket Connection and Event Broadcasting Manager.
Distributes live stream telemetry and emergency incident alerts to connected operators.
"""

import json
from typing import List, Dict, Any
from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: Dict[str, Any]):
        """Broadcasts JSON payload to all active client connections."""
        dead_connections = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                dead_connections.append(connection)

        for dead in dead_connections:
            if dead in self.active_connections:
                self.active_connections.remove(dead)

    async def broadcast_incident(self, incident_data: Dict[str, Any]):
        await self.broadcast({
            "event_type": "EMERGENCY_INCIDENT_ALERT",
            "data": incident_data
        })

    async def broadcast_telemetry(self, telemetry_data: Dict[str, Any]):
        await self.broadcast({
            "event_type": "STREAM_TELEMETRY",
            "data": telemetry_data
        })


ws_manager = ConnectionManager()
