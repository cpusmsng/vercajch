from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel

from .common import BaseSchema


class LocationBase(BaseModel):
    name: str
    type: str  # warehouse, project, vehicle, other
    code: Optional[str] = None
    address: Optional[str] = None
    gps_lat: Optional[Decimal] = None
    gps_lng: Optional[Decimal] = None
    parent_location_id: Optional[UUID] = None
    responsible_user_id: Optional[UUID] = None
    is_active: bool = True


class LocationCreate(LocationBase):
    pass


class LocationUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    code: Optional[str] = None
    address: Optional[str] = None
    gps_lat: Optional[Decimal] = None
    gps_lng: Optional[Decimal] = None
    parent_location_id: Optional[UUID] = None
    responsible_user_id: Optional[UUID] = None
    is_active: Optional[bool] = None


class LocationResponse(BaseSchema):
    id: UUID
    name: str
    type: str
    code: Optional[str] = None
    address: Optional[str] = None
    gps_lat: Optional[Decimal] = None
    gps_lng: Optional[Decimal] = None
    parent_location_id: Optional[UUID] = None
    responsible_user_id: Optional[UUID] = None
    is_active: bool
    created_at: datetime


class LocationTree(LocationResponse):
    children: List["LocationTree"] = []


LocationTree.model_rebuild()
