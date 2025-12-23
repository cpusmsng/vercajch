from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel

from .common import BaseSchema
from .equipment import EquipmentListResponse


class CalibrationBase(BaseModel):
    calibration_type: str  # initial, periodic, after_repair, verification
    calibration_date: date
    valid_until: date
    next_calibration_date: Optional[date] = None
    performed_by_type: Optional[str] = None  # internal, external, manufacturer
    performed_by_name: Optional[str] = None
    calibration_lab: Optional[str] = None
    certificate_number: Optional[str] = None
    result: str  # passed, passed_with_adjustment, failed
    cost: Optional[Decimal] = None
    notes: Optional[str] = None


class CalibrationCreate(CalibrationBase):
    pass


class CalibrationUpdate(BaseModel):
    calibration_type: Optional[str] = None
    calibration_date: Optional[date] = None
    valid_until: Optional[date] = None
    next_calibration_date: Optional[date] = None
    performed_by_type: Optional[str] = None
    performed_by_name: Optional[str] = None
    calibration_lab: Optional[str] = None
    certificate_number: Optional[str] = None
    result: Optional[str] = None
    cost: Optional[Decimal] = None
    notes: Optional[str] = None


class CalibrationResponse(BaseSchema):
    id: UUID
    equipment_id: UUID
    calibration_type: str
    calibration_date: date
    valid_until: date
    next_calibration_date: Optional[date] = None
    performed_by_type: Optional[str] = None
    performed_by_name: Optional[str] = None
    calibration_lab: Optional[str] = None
    certificate_number: Optional[str] = None
    certificate_url: Optional[str] = None
    result: str
    cost: Optional[Decimal] = None
    notes: Optional[str] = None
    days_until_expiry: Optional[int] = None
    status: Optional[str] = None  # valid, expiring, expired
    created_at: datetime


class CalibrationSummary(BaseModel):
    total_requiring_calibration: int
    valid: int
    expiring_30_days: int
    expiring_7_days: int
    expired: int


class CalibrationDueItem(BaseModel):
    equipment: EquipmentListResponse
    days_until_expiry: int
    last_calibration: Optional[CalibrationResponse] = None


class CalibrationDashboard(BaseModel):
    summary: CalibrationSummary
    upcoming: List[CalibrationDueItem]
    expired: List[CalibrationDueItem]
    monthly_forecast: Optional[dict] = None


class CalibrationReminderSettingCreate(BaseModel):
    scope_type: str  # global, category, equipment
    category_id: Optional[UUID] = None
    equipment_id: Optional[UUID] = None
    days_before: List[int] = [30, 14, 7, 1]
    notify_holder: bool = True
    notify_manager: bool = True
    notify_users: Optional[List[UUID]] = None
    notify_push: bool = True
    notify_email: bool = True
    notify_in_app: bool = True
    is_active: bool = True


class CalibrationReminderSettingResponse(BaseSchema):
    id: UUID
    scope_type: str
    category_id: Optional[UUID] = None
    equipment_id: Optional[UUID] = None
    days_before: List[int]
    notify_holder: bool
    notify_manager: bool
    notify_users: Optional[List[UUID]] = None
    notify_push: bool
    notify_email: bool
    notify_in_app: bool
    is_active: bool
    created_at: datetime
