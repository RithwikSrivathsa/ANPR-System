import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.services.realtime import ConnectionHeartbeat

router = APIRouter()


@router.websocket("/ws/detections")
async def websocket_detections(websocket: WebSocket):
    broker = websocket.app.state.realtime
    await broker.register(websocket)
    heartbeat = asyncio.create_task(ConnectionHeartbeat(websocket).keepalive())
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        heartbeat.cancel()
        broker.unregister(websocket)
