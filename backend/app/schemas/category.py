from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel

from .common import BaseSchema


class CategoryBase(BaseModel):
    name: str
    code: Optional[str] = None
    parent_category_id: Optional[UUID] = None
    default_maintenance_interval_days: Optional[int] = None
    requires_certification: bool = False
    transfer_requires_approval: bool = False
    max_transfer_days: Optional[int] = None
    icon: Optional[str] = None
    color: Optional[str] = None


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    parent_category_id: Optional[UUID] = None
    default_maintenance_interval_days: Optional[int] = None
    requires_certification: Optional[bool] = None
    transfer_requires_approval: Optional[bool] = None
    max_transfer_days: Optional[int] = None
    icon: Optional[str] = None
    color: Optional[str] = None


class CategoryResponse(BaseSchema):
    id: UUID
    name: str
    code: Optional[str] = None
    parent_category_id: Optional[UUID] = None
    default_maintenance_interval_days: Optional[int] = None
    requires_certification: bool
    transfer_requires_approval: bool
    max_transfer_days: Optional[int] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    created_at: datetime


class CategoryTree(CategoryResponse):
    children: List["CategoryTree"] = []


CategoryTree.model_rebuild()
