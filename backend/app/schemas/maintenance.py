from datetime import datetime, date
from decimal import Decimal
from typing import Optional
from uuid import UUID
from pydantic import BaseModel

from .common import BaseSchema
from .equipment import EquipmentListResponse, UserBasic


class MaintenanceBase(BaseModel):
    equipment_id: UUID
    type: str  # scheduled, repair, inspection, calibration
    status: str = "pending"  # pending, in_progress, completed, cancelled
    priority: str = "normal"  # low, normal, high, urgent
    title: Optional[str] = None
    description: Optional[str] = None
    scheduled_date: Optional[date] = None
    assigned_to: Optional[UUID] = None
    vendor: Optional[str] = None
    notes: Optional[str] = None


class MaintenanceCreate(MaintenanceBase):
    pass


class MaintenanceUpdate(BaseModel):
    type: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    scheduled_date: Optional[date] = None
    assigned_to: Optional[UUID] = None
    cost: Optional[Decimal] = None
    vendor: Optional[str] = None
    next_maintenance_date: Optional[date] = None
    notes: Optional[str] = None


class MaintenanceComplete(BaseModel):
    cost: Optional[Decimal] = None
    next_maintenance_date: Optional[date] = None
    notes: Optional[str] = None


class MaintenanceResponse(BaseSchema):
    id: UUID
    equipment_id: UUID
    equipment: Optional[EquipmentListResponse] = None
    type: str
    status: str
    priority: str
    title: Optional[str] = None
    description: Optional[str] = None
    scheduled_date: Optional[date] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    performed_by: Optional[UUID] = None
    performer: Optional[UserBasic] = None
    assigned_to: Optional[UUID] = None
    assignee: Optional[UserBasic] = None
    cost: Optional[Decimal] = None
    vendor: Optional[str] = None
    next_maintenance_date: Optional[date] = None
    notes: Optional[str] = None
    created_at: datetime
