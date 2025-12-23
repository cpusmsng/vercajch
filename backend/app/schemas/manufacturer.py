from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel

from .common import BaseSchema


class ManufacturerBase(BaseModel):
    name: str
    website: Optional[str] = None
    support_email: Optional[str] = None
    support_phone: Optional[str] = None
    logo_url: Optional[str] = None
    is_active: bool = True


class ManufacturerCreate(ManufacturerBase):
    pass


class ManufacturerResponse(BaseSchema):
    id: UUID
    name: str
    website: Optional[str] = None
    support_email: Optional[str] = None
    support_phone: Optional[str] = None
    logo_url: Optional[str] = None
    is_active: bool
    created_at: datetime


class EquipmentModelBase(BaseModel):
    manufacturer_id: Optional[UUID] = None
    category_id: Optional[UUID] = None
    name: str
    full_name: Optional[str] = None
    default_calibration_interval_days: Optional[int] = None
    requires_calibration: bool = False
    manual_url: Optional[str] = None
    specifications: Optional[dict] = None
    is_active: bool = True


class EquipmentModelCreate(EquipmentModelBase):
    pass


class EquipmentModelResponse(BaseSchema):
    id: UUID
    manufacturer_id: Optional[UUID] = None
    category_id: Optional[UUID] = None
    name: str
    full_name: Optional[str] = None
    default_calibration_interval_days: Optional[int] = None
    requires_calibration: bool
    manual_url: Optional[str] = None
    specifications: Optional[dict] = None
    is_active: bool
    created_at: datetime
