from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, status, Query
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.api.deps import DB, CurrentUser, ManagerUser, AdminUser
from app.core.security import get_password_hash
from app.core.permissions import Permission
from app.models.user import User, Role, Department
from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserListResponse
from app.schemas.common import PaginatedResponse

router = APIRouter()


@router.get("", response_model=PaginatedResponse[UserListResponse])
async def list_users(
    db: DB,
    current_user: CurrentUser,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    department_id: Optional[UUID] = None,
    role_id: Optional[UUID] = None,
    is_active: Optional[bool] = None,
):
    """List users with pagination and filters"""
    query = select(User).options(selectinload(User.role), selectinload(User.department))

    # Apply filters
    if search:
        query = query.where(
            (User.full_name.ilike(f"%{search}%")) |
            (User.email.ilike(f"%{search}%"))
        )
    if department_id:
        query = query.where(User.department_id == department_id)
    if role_id:
        query = query.where(User.role_id == role_id)
    if is_active is not None:
        query = query.where(User.is_active == is_active)

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    # Paginate
    query = query.offset((page - 1) * size).limit(size).order_by(User.full_name)
    result = await db.execute(query)
    users = result.scalars().all()

    return PaginatedResponse(
        items=[UserListResponse.model_validate(u) for u in users],
        total=total,
        page=page,
        size=size,
        pages=(total + size - 1) // size
    )


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: DB,
    current_user: ManagerUser,
):
    """Create a new user"""
    # Check if email already exists
    existing = await db.execute(
        select(User).where(User.email == user_data.email)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    user = User(
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        phone=user_data.phone,
        employee_number=user_data.employee_number,
        role_id=user_data.role_id,
        department_id=user_data.department_id,
        manager_id=user_data.manager_id,
        is_active=user_data.is_active,
        can_access_web=user_data.can_access_web,
        can_access_mobile=user_data.can_access_mobile,
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return UserResponse.model_validate(user)


@router.put("/me", response_model=UserResponse)
async def update_my_profile(
    profile_data: UserUpdate,
    db: DB,
    current_user: CurrentUser,
):
    """Update current user's profile (only name and phone)"""
    # Reload user with relationships
    result = await db.execute(
        select(User)
        .options(selectinload(User.role), selectinload(User.department))
        .where(User.id == current_user.id)
    )
    user = result.scalar_one()

    # Only allow updating name and phone for self-service
    if profile_data.full_name is not None:
        user.full_name = profile_data.full_name
    if profile_data.phone is not None:
        user.phone = profile_data.phone

    await db.commit()
    await db.refresh(user)

    return UserResponse.model_validate(user)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    db: DB,
    current_user: CurrentUser,
):
    """Get user by ID"""
    result = await db.execute(
        select(User)
        .options(selectinload(User.role), selectinload(User.department))
        .where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return UserResponse.model_validate(user)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    user_data: UserUpdate,
    db: DB,
    current_user: ManagerUser,
):
    """Update a user"""
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    update_data = user_data.model_dump(exclude_unset=True)

    if "password" in update_data:
        update_data["password_hash"] = get_password_hash(update_data.pop("password"))

    if "email" in update_data and update_data["email"] != user.email:
        existing = await db.execute(
            select(User).where(User.email == update_data["email"])
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

    for field, value in update_data.items():
        setattr(user, field, value)

    await db.commit()
    await db.refresh(user)

    return UserResponse.model_validate(user)


@router.delete("/{user_id}")
async def delete_user(
    user_id: UUID,
    db: DB,
    current_user: AdminUser,
):
    """Deactivate a user"""
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user.is_active = False
    await db.commit()

    return {"message": "User deactivated successfully"}


@router.get("/{user_id}/equipment")
async def get_user_equipment(
    user_id: UUID,
    db: DB,
    current_user: CurrentUser,
):
    """Get equipment assigned to user"""
    from app.models.equipment import Equipment
    from app.schemas.equipment import EquipmentListResponse

    result = await db.execute(
        select(Equipment)
        .options(
            selectinload(Equipment.category),
            selectinload(Equipment.current_location)
        )
        .where(Equipment.current_holder_id == user_id)
        .order_by(Equipment.name)
    )
    equipment = result.scalars().all()

    return [EquipmentListResponse.model_validate(e) for e in equipment]


@router.get("/team", response_model=List[UserListResponse])
async def get_team(
    db: DB,
    current_user: CurrentUser,
):
    """Get current user's team members"""
    result = await db.execute(
        select(User)
        .options(selectinload(User.role), selectinload(User.department))
        .where(User.manager_id == current_user.id)
        .order_by(User.full_name)
    )
    users = result.scalars().all()

    return [UserListResponse.model_validate(u) for u in users]
