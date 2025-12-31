import uuid as uuid_module
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, status, Query
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.api.deps import DB, CurrentUser, ManagerUser
from app.core.config import settings
from app.models.equipment import Equipment, EquipmentTag
from app.schemas.equipment import EquipmentTagResponse, EquipmentTagCreate, EquipmentResponse
from app.schemas.common import PaginatedResponse

router = APIRouter()


@router.get("", response_model=PaginatedResponse[EquipmentTagResponse])
async def list_tags(
    db: DB,
    current_user: CurrentUser,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    tag_type: Optional[str] = None,
    status: Optional[str] = None,
    unassigned: Optional[bool] = None,
):
    """List tags with filters"""
    query = select(EquipmentTag)

    if tag_type:
        query = query.where(EquipmentTag.tag_type == tag_type)
    if status:
        query = query.where(EquipmentTag.status == status)
    if unassigned:
        query = query.where(EquipmentTag.equipment_id.is_(None))

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    # Paginate
    query = query.offset((page - 1) * size).limit(size).order_by(EquipmentTag.created_at.desc())
    result = await db.execute(query)
    tags = result.scalars().all()

    return PaginatedResponse(
        items=[EquipmentTagResponse.model_validate(t) for t in tags],
        total=total,
        page=page,
        size=size,
        pages=(total + size - 1) // size
    )


@router.post("/generate", response_model=List[EquipmentTagResponse])
async def generate_tags(
    count: int = Query(1, ge=1, le=100),
    tag_type: str = "qr_code",
    db: DB = None,
    current_user: ManagerUser = None,
):
    """Generate new QR codes/tags"""
    batch_id = uuid_module.uuid4()
    tags = []

    for i in range(count):
        tag_uuid = uuid_module.uuid4()
        tag_value = f"{settings.QR_BASE_URL}/{tag_uuid}"

        tag = EquipmentTag(
            tag_type=tag_type,
            tag_value=tag_value,
            status="active",
            batch_id=batch_id,
            created_by=current_user.id
        )
        db.add(tag)
        tags.append(tag)

    await db.commit()

    for tag in tags:
        await db.refresh(tag)

    return [EquipmentTagResponse.model_validate(t) for t in tags]


@router.get("/lookup")
async def lookup_tag(
    value: str,
    db: DB,
    current_user: CurrentUser,
):
    """Lookup equipment by tag value"""
    result = await db.execute(
        select(EquipmentTag)
        .options(
            selectinload(EquipmentTag.equipment).options(
                selectinload(Equipment.category),
                selectinload(Equipment.current_location),
                selectinload(Equipment.current_holder)
            )
        )
        .where(EquipmentTag.tag_value == value)
    )
    tag = result.scalar_one_or_none()

    if not tag:
        # Try RFID UID lookup
        result = await db.execute(
            select(EquipmentTag)
            .options(
                selectinload(EquipmentTag.equipment).options(
                    selectinload(Equipment.category),
                    selectinload(Equipment.current_location),
                    selectinload(Equipment.current_holder)
                )
            )
            .where(EquipmentTag.rfid_uid == value)
        )
        tag = result.scalar_one_or_none()

    if not tag:
        # Tag not found - return response for onboarding new equipment
        return {
            "found": False,
            "tag_value": value,
            "equipment": None
        }

    # Update scan count
    tag.scan_count += 1
    tag.last_scanned_at = datetime.utcnow()
    await db.commit()

    if tag.equipment:
        return {
            "found": True,
            "tag": EquipmentTagResponse.model_validate(tag),
            "equipment": EquipmentResponse.model_validate(tag.equipment)
        }
    else:
        return {
            "found": True,
            "tag": EquipmentTagResponse.model_validate(tag),
            "equipment": None
        }


@router.post("/{tag_id}/assign")
async def assign_tag(
    tag_id: UUID,
    equipment_id: UUID,
    db: DB,
    current_user: ManagerUser,
):
    """Assign tag to equipment"""
    # Get tag
    tag_result = await db.execute(
        select(EquipmentTag).where(EquipmentTag.id == tag_id)
    )
    tag = tag_result.scalar_one_or_none()

    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )

    if tag.equipment_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tag is already assigned"
        )

    # Get equipment
    eq_result = await db.execute(
        select(Equipment).where(Equipment.id == equipment_id)
    )
    equipment = eq_result.scalar_one_or_none()

    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment not found"
        )

    tag.equipment_id = equipment_id
    tag.applied_at = datetime.utcnow()

    await db.commit()

    return {"message": "Tag assigned successfully"}


@router.post("/{tag_id}/replace")
async def replace_tag(
    tag_id: UUID,
    new_tag_data: EquipmentTagCreate,
    db: DB,
    current_user: ManagerUser,
):
    """Replace damaged tag with new one"""
    # Get old tag
    old_tag_result = await db.execute(
        select(EquipmentTag).where(EquipmentTag.id == tag_id)
    )
    old_tag = old_tag_result.scalar_one_or_none()

    if not old_tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )

    if not old_tag.equipment_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tag is not assigned to any equipment"
        )

    equipment_id = old_tag.equipment_id

    # Mark old tag as replaced
    old_tag.status = "replaced"
    old_tag.equipment_id = None

    # Create new tag
    new_tag = EquipmentTag(
        equipment_id=equipment_id,
        tag_type=new_tag_data.tag_type,
        tag_value=new_tag_data.tag_value,
        rfid_uid=new_tag_data.rfid_uid,
        status="active",
        applied_at=datetime.utcnow(),
        created_by=current_user.id
    )
    db.add(new_tag)

    await db.commit()
    await db.refresh(new_tag)

    return {
        "message": "Tag replaced successfully",
        "new_tag": EquipmentTagResponse.model_validate(new_tag)
    }


@router.post("/rfid/register")
async def register_rfid(
    rfid_uid: str,
    rfid_technology: Optional[str] = None,
    equipment_id: Optional[UUID] = None,
    db: DB = None,
    current_user: ManagerUser = None,
):
    """Register RFID tag"""
    # Check if RFID already exists
    existing = await db.execute(
        select(EquipmentTag).where(EquipmentTag.rfid_uid == rfid_uid)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="RFID UID already registered"
        )

    tag_uuid = uuid_module.uuid4()
    tag = EquipmentTag(
        equipment_id=equipment_id,
        tag_type="rfid_nfc",
        tag_value=f"{settings.QR_BASE_URL}/{tag_uuid}",
        rfid_uid=rfid_uid,
        rfid_technology=rfid_technology,
        status="active",
        created_by=current_user.id,
        applied_at=datetime.utcnow() if equipment_id else None
    )

    db.add(tag)
    await db.commit()
    await db.refresh(tag)

    return EquipmentTagResponse.model_validate(tag)


@router.post("/rfid/bulk-scan")
async def bulk_rfid_scan(
    rfid_uids: List[str],
    db: DB,
    current_user: CurrentUser,
):
    """Bulk RFID scan for inventory"""
    result = await db.execute(
        select(EquipmentTag)
        .options(
            selectinload(EquipmentTag.equipment).options(
                selectinload(Equipment.category),
                selectinload(Equipment.current_holder)
            )
        )
        .where(EquipmentTag.rfid_uid.in_(rfid_uids))
    )
    tags = result.scalars().all()

    found = []
    not_found = []

    found_uids = {tag.rfid_uid for tag in tags}

    for uid in rfid_uids:
        if uid in found_uids:
            tag = next(t for t in tags if t.rfid_uid == uid)
            tag.scan_count += 1
            tag.last_scanned_at = datetime.utcnow()
            found.append({
                "rfid_uid": uid,
                "tag": EquipmentTagResponse.model_validate(tag),
                "equipment": EquipmentResponse.model_validate(tag.equipment) if tag.equipment else None
            })
        else:
            not_found.append(uid)

    await db.commit()

    return {
        "found": found,
        "not_found": not_found,
        "total_scanned": len(rfid_uids),
        "total_found": len(found)
    }
