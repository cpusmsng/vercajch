from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID
from pydantic import BaseModel

from .common import BaseSchema
from .equipment import EquipmentListResponse, UserBasic, LocationBasic


class CheckoutCreate(BaseModel):
    equipment_id: UUID
    user_id: Optional[UUID] = None  # If not provided, use current user
    location_id: Optional[UUID] = None
    expected_return_at: Optional[datetime] = None
    condition: Optional[str] = None
    photo_url: Optional[str] = None
    notes: Optional[str] = None
    gps_lat: Optional[Decimal] = None
    gps_lng: Optional[Decimal] = None


class CheckoutReturn(BaseModel):
    condition: Optional[str] = None
    photo_url: Optional[str] = None
    notes: Optional[str] = None
    gps_lat: Optional[Decimal] = None
    gps_lng: Optional[Decimal] = None


class CheckoutExtend(BaseModel):
    expected_return_at: datetime
    reason: Optional[str] = None


class CheckoutResponse(BaseSchema):
    id: UUID
    equipment_id: UUID
    equipment: Optional[EquipmentListResponse] = None
    user_id: UUID
    user: Optional[UserBasic] = None
    location_id: Optional[UUID] = None
    location: Optional[LocationBasic] = None
    checkout_at: datetime
    expected_return_at: Optional[datetime] = None
    actual_return_at: Optional[datetime] = None
    checkout_condition: Optional[str] = None
    checkout_notes: Optional[str] = None
    return_condition: Optional[str] = None
    return_notes: Optional[str] = None
    status: str
    created_at: datetime
