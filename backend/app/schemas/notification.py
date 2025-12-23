from datetime import datetime
from typing import Optional
from uuid import UUID

from .common import BaseSchema


class NotificationResponse(BaseSchema):
    id: UUID
    type: str
    title: str
    message: Optional[str] = None
    related_entity_type: Optional[str] = None
    related_entity_id: Optional[UUID] = None
    is_read: bool
    read_at: Optional[datetime] = None
    created_at: datetime
