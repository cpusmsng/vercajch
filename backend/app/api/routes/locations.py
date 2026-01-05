from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, status, Query
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.api.deps import DB, CurrentUser, ManagerUser, AdminUser
from app.models.equipment import Location, Equipment
from app.schemas.location import LocationCreate, LocationUpdate, LocationResponse, LocationTree
from app.schemas.equipment import EquipmentListResponse

router = APIRouter()


@router.get("", response_model=List[LocationResponse])
async def list_locations(
    db: DB,
    current_user: CurrentUser,
    type: Optional[str] = None,
    parent_id: Optional[UUID] = None,
    is_active: Optional[bool] = True,
):
    """List locations"""
    query = select(Location)

    if type:
        query = query.where(Location.type == type)
    if parent_id:
        query = query.where(Location.parent_location_id == parent_id)
    if is_active is not None:
        query = query.where(Location.is_active == is_active)

    query = query.order_by(Location.name)
    result = await db.execute(query)
    locations = result.scalars().all()

    return [LocationResponse.model_validate(loc) for loc in locations]


@router.get("/tree", response_model=List[LocationTree])
async def get_location_tree(
    db: DB,
    current_user: CurrentUser,
):
    """Get location tree structure"""
    result = await db.execute(
        select(Location)
        .where(Location.parent_location_id.is_(None))
        .order_by(Location.name)
    )
    root_locations = result.scalars().all()

    async def build_tree(location: Location) -> LocationTree:
        children_result = await db.execute(
            select(Location)
            .where(Location.parent_location_id == location.id)
            .order_by(Location.name)
        )
        children = children_result.scalars().all()

        return LocationTree(
            id=location.id,
            name=location.name,
            type=location.type,
            code=location.code,
            address=location.address,
            gps_lat=location.gps_lat,
            gps_lng=location.gps_lng,
            parent_location_id=location.parent_location_id,
            responsible_user_id=location.responsible_user_id,
            is_active=location.is_active,
            created_at=location.created_at,
            children=[await build_tree(c) for c in children]
        )

    return [await build_tree(loc) for loc in root_locations]


@router.post("", response_model=LocationResponse, status_code=status.HTTP_201_CREATED)
async def create_location(
    location_data: LocationCreate,
    db: DB,
    current_user: ManagerUser,
):
    """Create a new location"""
    location = Location(**location_data.model_dump())
    db.add(location)
    await db.commit()
    await db.refresh(location)

    return LocationResponse.model_validate(location)


@router.get("/{location_id}", response_model=LocationResponse)
async def get_location(
    location_id: UUID,
    db: DB,
    current_user: CurrentUser,
):
    """Get location by ID"""
    result = await db.execute(
        select(Location).where(Location.id == location_id)
    )
    location = result.scalar_one_or_none()

    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location not found"
        )

    return LocationResponse.model_validate(location)


@router.put("/{location_id}", response_model=LocationResponse)
@router.patch("/{location_id}", response_model=LocationResponse)
async def update_location(
    location_id: UUID,
    location_data: LocationUpdate,
    db: DB,
    current_user: ManagerUser,
):
    """Update a location"""
    result = await db.execute(
        select(Location).where(Location.id == location_id)
    )
    location = result.scalar_one_or_none()

    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location not found"
        )

    update_data = location_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(location, field, value)

    await db.commit()
    await db.refresh(location)

    return LocationResponse.model_validate(location)


@router.delete("/{location_id}")
async def delete_location(
    location_id: UUID,
    db: DB,
    current_user: AdminUser,
):
    """Delete a location"""
    result = await db.execute(
        select(Location).where(Location.id == location_id)
    )
    location = result.scalar_one_or_none()

    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location not found"
        )

    # Soft delete - just deactivate
    location.is_active = False
    await db.commit()

    return {"message": "Location deactivated successfully"}


@router.get("/{location_id}/equipment", response_model=List[EquipmentListResponse])
async def get_location_equipment(
    location_id: UUID,
    db: DB,
    current_user: CurrentUser,
):
    """Get equipment at location"""
    result = await db.execute(
        select(Equipment)
        .options(
            selectinload(Equipment.category),
            selectinload(Equipment.current_holder)
        )
        .where(Equipment.current_location_id == location_id)
        .order_by(Equipment.name)
    )
    equipment = result.scalars().all()

    return [EquipmentListResponse.model_validate(e) for e in equipment]
