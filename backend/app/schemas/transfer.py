from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel

from .common import BaseSchema
from .equipment import EquipmentListResponse, UserBasic, LocationBasic, CategoryBasic


class TransferRequestCreate(BaseModel):
    request_type: str  # direct, broadcast
    equipment_id: Optional[UUID] = None  # For direct
    category_id: Optional[UUID] = None  # For broadcast
    holder_id: Optional[UUID] = None  # For direct
    location_id: Optional[UUID] = None
    location_note: Optional[str] = None
    needed_from: Optional[datetime] = None
    needed_until: Optional[datetime] = None
    message: Optional[str] = None


class TransferRequestRespond(BaseModel):
    action: str  # accept, reject
    message: Optional[str] = None
    rejection_reason: Optional[str] = None


class TransferOfferCreate(BaseModel):
    equipment_id: UUID
    message: Optional[str] = None


class TransferOfferResponse(BaseSchema):
    id: UUID
    request_id: UUID
    offerer_id: UUID
    offerer: Optional[UserBasic] = None
    equipment_id: UUID
    equipment: Optional[EquipmentListResponse] = None
    message: Optional[str] = None
    status: str
    created_at: datetime


class TransferRequestResponse(BaseSchema):
    id: UUID
    request_type: str
    equipment_id: Optional[UUID] = None
    equipment: Optional[EquipmentListResponse] = None
    category_id: Optional[UUID] = None
    category: Optional[CategoryBasic] = None
    requester_id: UUID
    requester: Optional[UserBasic] = None
    holder_id: Optional[UUID] = None
    holder: Optional[UserBasic] = None
    location_id: Optional[UUID] = None
    location: Optional[LocationBasic] = None
    location_note: Optional[str] = None
    needed_from: Optional[datetime] = None
    needed_until: Optional[datetime] = None
    message: Optional[str] = None
    status: str
    requires_leader_approval: bool
    approved_by: Optional[UUID] = None
    approved_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    responded_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    created_at: datetime
    offers: List[TransferOfferResponse] = []


class TransferConfirmation(BaseModel):
    condition: Optional[str] = None
    photo_url: Optional[str] = None
    notes: Optional[str] = None
    gps_lat: Optional[Decimal] = None
    gps_lng: Optional[Decimal] = None


class TransferApproval(BaseModel):
    approved: bool
    notes: Optional[str] = None


class TransferResponse(BaseSchema):
    id: UUID
    equipment_id: UUID
    equipment: Optional[EquipmentListResponse] = None
    request_id: Optional[UUID] = None
    from_user_id: UUID
    from_user: Optional[UserBasic] = None
    to_user_id: UUID
    to_user: Optional[UserBasic] = None
    location_id: Optional[UUID] = None
    location: Optional[LocationBasic] = None
    from_confirmed_at: Optional[datetime] = None
    to_confirmed_at: Optional[datetime] = None
    condition_at_transfer: Optional[str] = None
    photo_url: Optional[str] = None
    notes: Optional[str] = None
    transfer_type: str
    created_at: datetime
