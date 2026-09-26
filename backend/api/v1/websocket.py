"""
FIREGUARD AI - Real-time WebSocket & SSE Updates (Requirement 17)
Broadcasts live thermal detections, incident updates, and alerts to tactical command centers.
"""
import asyncio
import json
from typing import List, Dict, Any
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse

router = APIRouter(tags=["Real-time Feeds"])

class ConnectionManager:
    """Manages active WebSocket connections for live broadcasting."""
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: Dict[str, Any]):
        dead_connections = []
        payload = json.dumps(message)
        for connection in self.active_connections:
            try:
                await connection.send_text(payload)
            except Exception:
                dead_connections.append(connection)
        for dead in dead_connections:
            self.disconnect(dead)

manager = ConnectionManager()

# Global broadcast helper that can be called synchronously
def broadcast_realtime_event(event_type: str, data: Dict[str, Any]):
    message = {
        "event": event_type,
        "payload": data
    }
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.create_task(manager.broadcast(message))
        else:
            loop.run_until_complete(manager.broadcast(message))
    except Exception:
        pass

@router.websocket("/ws/hotspots")
async def websocket_hotspots(websocket: WebSocket):
    """
    WebSocket endpoint streaming live thermal hotspots and alerts without page refresh.
    """
    await manager.connect(websocket)
    try:
        # Send initial connection confirmation
        await websocket.send_text(json.dumps({
            "event": "CONNECTED",
            "message": "Connected to FIREGUARD AI Real-time Mission Stream",
            "protocol": "WebSocket v2.0"
        }))
        while True:
            # Keep connection alive, listen for ping or filter updates
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text(json.dumps({"event": "pong"}))
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:
        manager.disconnect(websocket)

@router.get("/events", summary="Server-Sent Events (SSE) stream for real-time telemetry")
async def server_sent_events():
    """
    SSE stream fallback for browsers or environments without WebSocket access.
    """
    async def event_generator():
        yield f"event: connected\ndata: {json.dumps({'status': 'STREAM_ACTIVE'})}\n\n"
        while True:
            await asyncio.sleep(15)
            heartbeat = {"type": "HEARTBEAT", "timestamp": asyncio.get_event_loop().time()}
            yield f"event: heartbeat\ndata: {json.dumps(heartbeat)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
