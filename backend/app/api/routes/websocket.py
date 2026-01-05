"""WebSocket endpoint for real-time notifications"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, HTTPException, status
from jose import jwt, JWTError
from typing import Optional

from app.core.config import settings
from app.core.websocket import manager

router = APIRouter()


async def get_user_from_token(token: str) -> Optional[str]:
    """Extract user ID from JWT token"""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
        return user_id
    except JWTError:
        return None


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(..., description="JWT authentication token")
):
    """
    WebSocket endpoint for real-time notifications.

    Connect with: ws://host/api/v1/ws?token=<jwt_token>

    Message format for subscriptions:
    {
        "action": "subscribe",
        "topic": "equipment"  # or "transfers", "maintenance", etc.
    }

    Notification format:
    {
        "type": "equipment.updated",
        "entity_type": "equipment",
        "entity_id": "uuid",
        "data": {...},
        "actor_id": "uuid",
        "timestamp": "iso-date"
    }
    """
    # Authenticate user
    user_id = await get_user_from_token(token)
    if not user_id:
        await websocket.close(code=4001, reason="Invalid token")
        return

    # Connect
    await manager.connect(websocket, user_id)

    # Subscribe to personal notifications by default
    manager.subscribe_to_topic(websocket, f"user:{user_id}")

    try:
        while True:
            # Receive messages (for subscription management)
            data = await websocket.receive_json()

            action = data.get("action")
            topic = data.get("topic")

            if action == "subscribe" and topic:
                manager.subscribe_to_topic(websocket, topic)
                await websocket.send_json({
                    "type": "subscribed",
                    "topic": topic
                })

            elif action == "unsubscribe" and topic:
                manager.unsubscribe_from_topic(websocket, topic)
                await websocket.send_json({
                    "type": "unsubscribed",
                    "topic": topic
                })

            elif action == "ping":
                await websocket.send_json({"type": "pong"})

    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
    except Exception:
        manager.disconnect(websocket, user_id)
