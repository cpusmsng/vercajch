from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, EmailStr

from .common import BaseSchema


class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    phone: Optional[str] = None
    employee_number: Optional[str] = None
    role_id: Optional[UUID] = None
    department_id: Optional[UUID] = None
    manager_id: Optional[UUID] = None
    is_active: bool = True
    can_access_web: bool = False
    can_access_mobile: bool = True


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    employee_number: Optional[str] = None
    role_id: Optional[UUID] = None
    department_id: Optional[UUID] = None
    manager_id: Optional[UUID] = None
    is_active: Optional[bool] = None
    can_access_web: Optional[bool] = None
    can_access_mobile: Optional[bool] = None
    password: Optional[str] = None


class RoleResponse(BaseSchema):
    id: UUID
    code: str
    name: str
    description: Optional[str] = None


class DepartmentResponse(BaseSchema):
    id: UUID
    name: str
    code: Optional[str] = None


class UserResponse(BaseSchema):
    id: UUID
    email: EmailStr
    full_name: str
    phone: Optional[str] = None
    employee_number: Optional[str] = None
    role_id: Optional[UUID] = None
    role: Optional[RoleResponse] = None
    department_id: Optional[UUID] = None
    department: Optional[DepartmentResponse] = None
    manager_id: Optional[UUID] = None
    is_active: bool
    can_access_web: bool
    can_access_mobile: bool
    avatar_url: Optional[str] = None
    last_login_at: Optional[datetime] = None
    last_login_platform: Optional[str] = None
    created_at: datetime


class UserListResponse(BaseSchema):
    id: UUID
    email: EmailStr
    full_name: str
    role: Optional[RoleResponse] = None
    department: Optional[DepartmentResponse] = None
    is_active: bool


class UserWithPermissions(UserResponse):
    permissions: List[str] = []
