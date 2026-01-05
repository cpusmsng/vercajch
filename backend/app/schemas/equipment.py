from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field

from .common import BaseSchema


class EquipmentBase(BaseModel):
    name: str
    description: Optional[str] = None
    category_id: Optional[UUID] = None
    model_id: Optional[UUID] = None
    serial_number: Optional[str] = None
    internal_code: Optional[str] = None
    manufacturer: Optional[str] = None
    model_name: Optional[str] = None
    purchase_date: Optional[date] = None
    purchase_price: Optional[Decimal] = None
    current_value: Optional[Decimal] = None
    warranty_expiry: Optional[date] = None
    condition: str = "good"
    status: str = "available"
    current_location_id: Optional[UUID] = None
    home_location_id: Optional[UUID] = None
    is_transferable: bool = True
    requires_calibration: bool = False
    calibration_interval_days: Optional[int] = None
    notes: Optional[str] = None
    custom_fields: Optional[dict] = None


class EquipmentCreate(EquipmentBase):
    pass


class EquipmentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[UUID] = None
    model_id: Optional[UUID] = None
    serial_number: Optional[str] = None
    internal_code: Optional[str] = None
    manufacturer: Optional[str] = None
    model_name: Optional[str] = None
    purchase_date: Optional[date] = None
    purchase_price: Optional[Decimal] = None
    current_value: Optional[Decimal] = None
    warranty_expiry: Optional[date] = None
    condition: Optional[str] = None
    status: Optional[str] = None
    current_location_id: Optional[UUID] = None
    home_location_id: Optional[UUID] = None
    is_transferable: Optional[bool] = None
    requires_calibration: Optional[bool] = None
    calibration_interval_days: Optional[int] = None
    notes: Optional[str] = None
    custom_fields: Optional[dict] = None


class CategoryBasic(BaseSchema):
    id: UUID
    name: str
    code: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None
    requires_certification: bool = Field(default=False)
    default_maintenance_interval_days: Optional[int] = Field(default=None)


class LocationBasic(BaseSchema):
    id: UUID
    name: str
    type: str
    code: Optional[str] = None
    address: Optional[str] = None
    gps_lat: Optional[float] = None
    gps_lng: Optional[float] = None


class UserBasic(BaseSchema):
    id: UUID
    full_name: str
    email: str


class EquipmentPhotoResponse(BaseSchema):
    id: UUID
    photo_type: str
    file_url: str
    thumbnail_url: Optional[str] = None
    description: Optional[str] = None
    sort_order: int


class EquipmentPhotoCreate(BaseModel):
    photo_type: str
    description: Optional[str] = None


class EquipmentTagResponse(BaseSchema):
    id: UUID
    tag_type: str
    tag_value: str
    rfid_uid: Optional[str] = None
    status: str
    scan_count: int
    last_scanned_at: Optional[datetime] = None


class EquipmentTagCreate(BaseModel):
    tag_type: str
    tag_value: str
    rfid_uid: Optional[str] = None


class EquipmentResponse(BaseSchema):
    id: UUID
    name: str
    description: Optional[str] = None
    category_id: Optional[UUID] = None
    category: Optional[CategoryBasic] = None
    model_id: Optional[UUID] = None
    serial_number: Optional[str] = None
    internal_code: Optional[str] = None
    manufacturer: Optional[str] = None
    model_name: Optional[str] = None
    purchase_date: Optional[date] = None
    purchase_price: Optional[Decimal] = None
    current_value: Optional[Decimal] = None
    warranty_expiry: Optional[date] = None
    condition: str
    status: str
    photo_url: Optional[str] = None
    current_location_id: Optional[UUID] = None
    current_location: Optional[LocationBasic] = None
    current_holder_id: Optional[UUID] = None
    current_holder: Optional[UserBasic] = None
    home_location_id: Optional[UUID] = None
    is_main_item: bool
    parent_equipment_id: Optional[UUID] = None
    is_transferable: bool
    requires_calibration: bool
    calibration_interval_days: Optional[int] = None
    last_calibration_date: Optional[date] = None
    next_calibration_date: Optional[date] = None
    calibration_status: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    tags: List[EquipmentTagResponse] = []
    photos: List[EquipmentPhotoResponse] = []


class EquipmentListResponse(BaseSchema):
    id: UUID
    name: str
    category: Optional[CategoryBasic] = None
    internal_code: Optional[str] = None
    condition: str
    status: str
    photo_url: Optional[str] = None
    current_location: Optional[LocationBasic] = None
    current_holder: Optional[UserBasic] = None
    calibration_status: Optional[str] = None
    next_calibration_date: Optional[date] = None


class EquipmentAccessory(BaseSchema):
    id: UUID
    name: str
    internal_code: Optional[str] = None
    condition: str
    photo_url: Optional[str] = None
