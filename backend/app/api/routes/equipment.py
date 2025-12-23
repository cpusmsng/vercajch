from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, status, Query, UploadFile, File
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.api.deps import DB, CurrentUser, ManagerUser, AdminUser
from app.core.permissions import Permission
from app.models.equipment import Equipment, EquipmentPhoto, EquipmentTag, Category, Location
from app.models.user import User
from app.schemas.equipment import (
    EquipmentCreate,
    EquipmentUpdate,
    EquipmentResponse,
    EquipmentListResponse,
    EquipmentPhotoResponse,
    EquipmentTagResponse,
    EquipmentAccessory,
)
from app.schemas.common import PaginatedResponse

router = APIRouter()


@router.get("", response_model=PaginatedResponse[EquipmentListResponse])
async def list_equipment(
    db: DB,
    current_user: CurrentUser,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    category_id: Optional[UUID] = None,
    status: Optional[str] = None,
    condition: Optional[str] = None,
    location_id: Optional[UUID] = None,
    holder_id: Optional[UUID] = None,
    requires_calibration: Optional[bool] = None,
    calibration_status: Optional[str] = None,
):
    """List equipment with pagination and filters"""
    query = select(Equipment).options(
        selectinload(Equipment.category),
        selectinload(Equipment.current_location),
        selectinload(Equipment.current_holder)
    )

    # Apply filters
    if search:
        query = query.where(
            (Equipment.name.ilike(f"%{search}%")) |
            (Equipment.internal_code.ilike(f"%{search}%")) |
            (Equipment.serial_number.ilike(f"%{search}%"))
        )
    if category_id:
        query = query.where(Equipment.category_id == category_id)
    if status:
        query = query.where(Equipment.status == status)
    if condition:
        query = query.where(Equipment.condition == condition)
    if location_id:
        query = query.where(Equipment.current_location_id == location_id)
    if holder_id:
        query = query.where(Equipment.current_holder_id == holder_id)
    if requires_calibration is not None:
        query = query.where(Equipment.requires_calibration == requires_calibration)
    if calibration_status:
        query = query.where(Equipment.calibration_status == calibration_status)

    # Only main items (not accessories)
    query = query.where(Equipment.is_main_item == True)

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    # Paginate
    query = query.offset((page - 1) * size).limit(size).order_by(Equipment.name)
    result = await db.execute(query)
    equipment = result.scalars().all()

    return PaginatedResponse(
        items=[EquipmentListResponse.model_validate(e) for e in equipment],
        total=total,
        page=page,
        size=size,
        pages=(total + size - 1) // size
    )


@router.post("", response_model=EquipmentResponse, status_code=status.HTTP_201_CREATED)
async def create_equipment(
    equipment_data: EquipmentCreate,
    db: DB,
    current_user: ManagerUser,
):
    """Create new equipment"""
    # Check internal_code uniqueness
    if equipment_data.internal_code:
        existing = await db.execute(
            select(Equipment).where(Equipment.internal_code == equipment_data.internal_code)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Internal code already exists"
            )

    equipment = Equipment(**equipment_data.model_dump())
    db.add(equipment)
    await db.commit()
    await db.refresh(equipment)

    return EquipmentResponse.model_validate(equipment)


@router.get("/{equipment_id}", response_model=EquipmentResponse)
async def get_equipment(
    equipment_id: UUID,
    db: DB,
    current_user: CurrentUser,
):
    """Get equipment by ID"""
    result = await db.execute(
        select(Equipment)
        .options(
            selectinload(Equipment.category),
            selectinload(Equipment.current_location),
            selectinload(Equipment.current_holder),
            selectinload(Equipment.tags),
            selectinload(Equipment.photos),
        )
        .where(Equipment.id == equipment_id)
    )
    equipment = result.scalar_one_or_none()

    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment not found"
        )

    return EquipmentResponse.model_validate(equipment)


@router.put("/{equipment_id}", response_model=EquipmentResponse)
async def update_equipment(
    equipment_id: UUID,
    equipment_data: EquipmentUpdate,
    db: DB,
    current_user: ManagerUser,
):
    """Update equipment"""
    result = await db.execute(
        select(Equipment).where(Equipment.id == equipment_id)
    )
    equipment = result.scalar_one_or_none()

    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment not found"
        )

    update_data = equipment_data.model_dump(exclude_unset=True)

    # Check internal_code uniqueness
    if "internal_code" in update_data and update_data["internal_code"] != equipment.internal_code:
        existing = await db.execute(
            select(Equipment).where(Equipment.internal_code == update_data["internal_code"])
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Internal code already exists"
            )

    for field, value in update_data.items():
        setattr(equipment, field, value)

    await db.commit()
    await db.refresh(equipment)

    return EquipmentResponse.model_validate(equipment)


@router.delete("/{equipment_id}")
async def delete_equipment(
    equipment_id: UUID,
    db: DB,
    current_user: AdminUser,
):
    """Delete equipment (set status to retired)"""
    result = await db.execute(
        select(Equipment).where(Equipment.id == equipment_id)
    )
    equipment = result.scalar_one_or_none()

    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment not found"
        )

    equipment.status = "retired"
    await db.commit()

    return {"message": "Equipment retired successfully"}


@router.get("/{equipment_id}/history")
async def get_equipment_history(
    equipment_id: UUID,
    db: DB,
    current_user: CurrentUser,
):
    """Get equipment checkout and maintenance history"""
    from app.models.checkout import Checkout
    from app.models.maintenance import MaintenanceRecord
    from app.schemas.checkout import CheckoutResponse
    from app.schemas.maintenance import MaintenanceResponse

    # Get checkouts
    checkout_result = await db.execute(
        select(Checkout)
        .options(selectinload(Checkout.user), selectinload(Checkout.location))
        .where(Checkout.equipment_id == equipment_id)
        .order_by(Checkout.checkout_at.desc())
        .limit(50)
    )
    checkouts = checkout_result.scalars().all()

    # Get maintenance records
    maintenance_result = await db.execute(
        select(MaintenanceRecord)
        .options(selectinload(MaintenanceRecord.performer))
        .where(MaintenanceRecord.equipment_id == equipment_id)
        .order_by(MaintenanceRecord.created_at.desc())
        .limit(50)
    )
    maintenance_records = maintenance_result.scalars().all()

    return {
        "checkouts": [CheckoutResponse.model_validate(c) for c in checkouts],
        "maintenance": [MaintenanceResponse.model_validate(m) for m in maintenance_records]
    }


# Photos
@router.get("/{equipment_id}/photos", response_model=List[EquipmentPhotoResponse])
async def get_equipment_photos(
    equipment_id: UUID,
    db: DB,
    current_user: CurrentUser,
):
    """Get equipment photos"""
    result = await db.execute(
        select(EquipmentPhoto)
        .where(EquipmentPhoto.equipment_id == equipment_id)
        .order_by(EquipmentPhoto.sort_order)
    )
    photos = result.scalars().all()
    return [EquipmentPhotoResponse.model_validate(p) for p in photos]


@router.post("/{equipment_id}/photos", response_model=EquipmentPhotoResponse)
async def upload_equipment_photo(
    equipment_id: UUID,
    photo_type: str,
    file: UploadFile = File(...),
    description: Optional[str] = None,
    db: DB = None,
    current_user: CurrentUser = None,
):
    """Upload equipment photo"""
    # TODO: Implement file upload to MinIO/S3
    # For now, return placeholder

    photo = EquipmentPhoto(
        equipment_id=equipment_id,
        photo_type=photo_type,
        file_url=f"/uploads/{equipment_id}/{file.filename}",
        description=description,
        uploaded_by=current_user.id,
        is_synced=True
    )

    db.add(photo)
    await db.commit()
    await db.refresh(photo)

    return EquipmentPhotoResponse.model_validate(photo)


@router.delete("/{equipment_id}/photos/{photo_id}")
async def delete_equipment_photo(
    equipment_id: UUID,
    photo_id: UUID,
    db: DB,
    current_user: ManagerUser,
):
    """Delete equipment photo"""
    result = await db.execute(
        select(EquipmentPhoto)
        .where(
            EquipmentPhoto.id == photo_id,
            EquipmentPhoto.equipment_id == equipment_id
        )
    )
    photo = result.scalar_one_or_none()

    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Photo not found"
        )

    await db.delete(photo)
    await db.commit()

    return {"message": "Photo deleted successfully"}


# Accessories
@router.get("/{equipment_id}/accessories", response_model=List[EquipmentAccessory])
async def get_equipment_accessories(
    equipment_id: UUID,
    db: DB,
    current_user: CurrentUser,
):
    """Get equipment accessories"""
    result = await db.execute(
        select(Equipment)
        .where(Equipment.parent_equipment_id == equipment_id)
        .order_by(Equipment.name)
    )
    accessories = result.scalars().all()
    return [EquipmentAccessory.model_validate(a) for a in accessories]


@router.post("/{equipment_id}/accessories", response_model=EquipmentAccessory)
async def add_equipment_accessory(
    equipment_id: UUID,
    accessory_data: EquipmentCreate,
    db: DB,
    current_user: ManagerUser,
):
    """Add accessory to equipment"""
    # Check parent exists
    result = await db.execute(
        select(Equipment).where(Equipment.id == equipment_id)
    )
    parent = result.scalar_one_or_none()

    if not parent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parent equipment not found"
        )

    accessory = Equipment(
        **accessory_data.model_dump(),
        parent_equipment_id=equipment_id,
        is_main_item=False,
        current_holder_id=parent.current_holder_id,
        current_location_id=parent.current_location_id
    )

    db.add(accessory)
    await db.commit()
    await db.refresh(accessory)

    return EquipmentAccessory.model_validate(accessory)
