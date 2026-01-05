"""WebSocket manager for real-time notifications"""
import json
from typing import Dict, Set, Optional
from uuid import UUID
from fastapi import WebSocket
from datetime import datetime


class ConnectionManager:
    """Manages WebSocket connections for real-time notifications"""

    def __init__(self):
        # Map of user_id -> set of WebSocket connections
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # Map of topic -> set of WebSocket connections (for broadcast)
        self.topic_subscriptions: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        """Accept connection and register it for the user"""
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)

    def disconnect(self, websocket: WebSocket, user_id: str):
        """Remove connection for user"""
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

        # Remove from all topic subscriptions
        for topic in list(self.topic_subscriptions.keys()):
            self.topic_subscriptions[topic].discard(websocket)
            if not self.topic_subscriptions[topic]:
                del self.topic_subscriptions[topic]

    def subscribe_to_topic(self, websocket: WebSocket, topic: str):
        """Subscribe a connection to a topic for broadcasts"""
        if topic not in self.topic_subscriptions:
            self.topic_subscriptions[topic] = set()
        self.topic_subscriptions[topic].add(websocket)

    def unsubscribe_from_topic(self, websocket: WebSocket, topic: str):
        """Unsubscribe a connection from a topic"""
        if topic in self.topic_subscriptions:
            self.topic_subscriptions[topic].discard(websocket)

    async def send_personal_message(self, message: dict, user_id: str):
        """Send message to specific user (all their connections)"""
        if user_id in self.active_connections:
            for connection in list(self.active_connections[user_id]):
                try:
                    await connection.send_json(message)
                except Exception:
                    # Connection might be closed, remove it
                    self.active_connections[user_id].discard(connection)

    async def broadcast_to_topic(self, message: dict, topic: str):
        """Broadcast message to all connections subscribed to a topic"""
        if topic in self.topic_subscriptions:
            for connection in list(self.topic_subscriptions[topic]):
                try:
                    await connection.send_json(message)
                except Exception:
                    # Connection might be closed, remove it
                    self.topic_subscriptions[topic].discard(connection)

    async def broadcast_all(self, message: dict):
        """Broadcast message to all connected users"""
        for user_id in list(self.active_connections.keys()):
            await self.send_personal_message(message, user_id)


# Global connection manager instance
manager = ConnectionManager()


# Event types for notifications
class EventType:
    # Equipment events
    EQUIPMENT_UPDATED = "equipment.updated"
    EQUIPMENT_CREATED = "equipment.created"
    EQUIPMENT_DELETED = "equipment.deleted"

    # Transfer events
    TRANSFER_REQUESTED = "transfer.requested"
    TRANSFER_ACCEPTED = "transfer.accepted"
    TRANSFER_REJECTED = "transfer.rejected"
    TRANSFER_HANDOVER_CONFIRMED = "transfer.handover_confirmed"
    TRANSFER_RECEIPT_CONFIRMED = "transfer.receipt_confirmed"
    TRANSFER_CANCELLED = "transfer.cancelled"

    # Checkout events
    CHECKOUT_CREATED = "checkout.created"
    CHECKOUT_RETURNED = "checkout.returned"

    # Maintenance events
    MAINTENANCE_SCHEDULED = "maintenance.scheduled"
    MAINTENANCE_COMPLETED = "maintenance.completed"


def create_notification(
    event_type: str,
    entity_type: str,
    entity_id: str,
    data: dict,
    actor_id: Optional[str] = None
) -> dict:
    """Create a standardized notification message"""
    return {
        "type": event_type,
        "entity_type": entity_type,
        "entity_id": entity_id,
        "data": data,
        "actor_id": actor_id,
        "timestamp": datetime.utcnow().isoformat()
    }
