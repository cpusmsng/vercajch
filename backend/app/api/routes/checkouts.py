from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, status, Query
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload

from app.api.deps import DB, CurrentUser, LeaderUser
from app.models.checkout import Checkout
from app.models.equipment import Equipment
from app.schemas.checkout import CheckoutCreate, CheckoutReturn, CheckoutExtend, CheckoutResponse
from app.schemas.common import PaginatedResponse

router = APIRouter()


@router.get("", response_model=PaginatedResponse[CheckoutResponse])
async def list_checkouts(
    db: DB,
    current_user: CurrentUser,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,  # active, returned, overdue
    user_id: Optional[UUID] = None,
    equipment_id: Optional[UUID] = None,
):
    """List checkouts with filters"""
    query = select(Checkout).options(
        selectinload(Checkout.equipment),
        selectinload(Checkout.user),
        selectinload(Checkout.location)
    )

    if status:
        query = query.where(Checkout.status == status)
    if user_id:
        query = query.where(Checkout.user_id == user_id)
    if equipment_id:
        query = query.where(Checkout.equipment_id == equipment_id)

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    # Paginate
    query = query.offset((page - 1) * size).limit(size).order_by(Checkout.checkout_at.desc())
    result = await db.execute(query)
    checkouts = result.scalars().all()

    return PaginatedResponse(
        items=[CheckoutResponse.model_validate(c) for c in checkouts],
        total=total,
        page=page,
        size=size,
        pages=(total + size - 1) // size
    )


@router.get("/active", response_model=List[CheckoutResponse])
async def get_active_checkouts(
    db: DB,
    current_user: CurrentUser,
    user_id: Optional[UUID] = None,
):
    """Get active checkouts"""
    query = select(Checkout).options(
        selectinload(Checkout.equipment),
        selectinload(Checkout.user),
        selectinload(Checkout.location)
    ).where(Checkout.status == "active")

    if user_id:
        query = query.where(Checkout.user_id == user_id)
    else:
        query = query.where(Checkout.user_id == current_user.id)

    query = query.order_by(Checkout.checkout_at.desc())
    result = await db.execute(query)
    checkouts = result.scalars().all()

    return [CheckoutResponse.model_validate(c) for c in checkouts]


@router.get("/overdue", response_model=List[CheckoutResponse])
async def get_overdue_checkouts(
    db: DB,
    current_user: LeaderUser,
):
    """Get overdue checkouts"""
    now = datetime.utcnow()
    result = await db.execute(
        select(Checkout)
        .options(
            selectinload(Checkout.equipment),
            selectinload(Checkout.user),
            selectinload(Checkout.location)
        )
        .where(
            and_(
                Checkout.status == "active",
                Checkout.expected_return_at < now
            )
        )
        .order_by(Checkout.expected_return_at)
    )
    checkouts = result.scalars().all()

    return [CheckoutResponse.model_validate(c) for c in checkouts]


@router.post("", response_model=CheckoutResponse, status_code=status.HTTP_201_CREATED)
async def create_checkout(
    checkout_data: CheckoutCreate,
    db: DB,
    current_user: CurrentUser,
):
    """Checkout equipment"""
    # Check equipment exists and is available
    eq_result = await db.execute(
        select(Equipment).where(Equipment.id == checkout_data.equipment_id)
    )
    equipment = eq_result.scalar_one_or_none()

    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment not found"
        )

    if equipment.status != "available":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Equipment is not available (status: {equipment.status})"
        )

    # Determine user
    user_id = checkout_data.user_id or current_user.id

    # Create checkout
    checkout = Checkout(
        equipment_id=checkout_data.equipment_id,
        user_id=user_id,
        location_id=checkout_data.location_id,
        expected_return_at=checkout_data.expected_return_at,
        checkout_condition=checkout_data.condition,
        checkout_photo_url=checkout_data.photo_url,
        checkout_notes=checkout_data.notes,
        checkout_gps_lat=checkout_data.gps_lat,
        checkout_gps_lng=checkout_data.gps_lng,
        checked_out_by=current_user.id,
        status="active"
    )

    db.add(checkout)

    # Update equipment
    equipment.status = "checked_out"
    equipment.current_holder_id = user_id
    if checkout_data.location_id:
        equipment.current_location_id = checkout_data.location_id

    await db.commit()
    await db.refresh(checkout)

    return CheckoutResponse.model_validate(checkout)


@router.put("/{checkout_id}/return", response_model=CheckoutResponse)
async def return_checkout(
    checkout_id: UUID,
    return_data: CheckoutReturn,
    db: DB,
    current_user: CurrentUser,
):
    """Return checked out equipment"""
    result = await db.execute(
        select(Checkout)
        .options(selectinload(Checkout.equipment))
        .where(Checkout.id == checkout_id)
    )
    checkout = result.scalar_one_or_none()

    if not checkout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Checkout not found"
        )

    if checkout.status != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Checkout is not active"
        )

    # Update checkout
    checkout.actual_return_at = datetime.utcnow()
    checkout.return_condition = return_data.condition
    checkout.return_photo_url = return_data.photo_url
    checkout.return_notes = return_data.notes
    checkout.return_gps_lat = return_data.gps_lat
    checkout.return_gps_lng = return_data.gps_lng
    checkout.checked_in_by = current_user.id
    checkout.status = "returned"

    # Update equipment
    equipment = checkout.equipment
    equipment.status = "available"
    equipment.current_holder_id = None
    if equipment.home_location_id:
        equipment.current_location_id = equipment.home_location_id
    if return_data.condition:
        equipment.condition = return_data.condition

    await db.commit()
    await db.refresh(checkout)

    return CheckoutResponse.model_validate(checkout)


@router.post("/{checkout_id}/extend", response_model=CheckoutResponse)
async def extend_checkout(
    checkout_id: UUID,
    extend_data: CheckoutExtend,
    db: DB,
    current_user: CurrentUser,
):
    """Extend checkout return date"""
    result = await db.execute(
        select(Checkout).where(Checkout.id == checkout_id)
    )
    checkout = result.scalar_one_or_none()

    if not checkout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Checkout not found"
        )

    if checkout.status != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Checkout is not active"
        )

    checkout.expected_return_at = extend_data.expected_return_at

    await db.commit()
    await db.refresh(checkout)

    return CheckoutResponse.model_validate(checkout)
