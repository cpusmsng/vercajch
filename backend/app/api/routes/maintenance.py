from datetime import datetime, date
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, status, Query
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload

from app.api.deps import DB, CurrentUser, LeaderUser, ManagerUser
from app.models.maintenance import MaintenanceRecord
from app.models.equipment import Equipment
from app.schemas.maintenance import (
    MaintenanceCreate,
    MaintenanceUpdate,
    MaintenanceComplete,
    MaintenanceResponse,
)
from app.schemas.common import PaginatedResponse

router = APIRouter()


@router.get("", response_model=PaginatedResponse[MaintenanceResponse])
async def list_maintenance(
    db: DB,
    current_user: CurrentUser,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    type: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    equipment_id: Optional[UUID] = None,
):
    """List maintenance records with filters"""
    query = select(MaintenanceRecord).options(
        selectinload(MaintenanceRecord.equipment),
        selectinload(MaintenanceRecord.performer),
        selectinload(MaintenanceRecord.assignee)
    )

    if type:
        query = query.where(MaintenanceRecord.type == type)
    if status:
        query = query.where(MaintenanceRecord.status == status)
    if priority:
        query = query.where(MaintenanceRecord.priority == priority)
    if equipment_id:
        query = query.where(MaintenanceRecord.equipment_id == equipment_id)

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    # Paginate
    query = query.offset((page - 1) * size).limit(size).order_by(MaintenanceRecord.created_at.desc())
    result = await db.execute(query)
    records = result.scalars().all()

    return PaginatedResponse(
        items=[MaintenanceResponse.model_validate(r) for r in records],
        total=total,
        page=page,
        size=size,
        pages=(total + size - 1) // size
    )


@router.post("", response_model=MaintenanceResponse, status_code=status.HTTP_201_CREATED)
async def create_maintenance(
    maintenance_data: MaintenanceCreate,
    db: DB,
    current_user: LeaderUser,
):
    """Create maintenance record"""
    # Verify equipment exists
    eq_result = await db.execute(
        select(Equipment).where(Equipment.id == maintenance_data.equipment_id)
    )
    equipment = eq_result.scalar_one_or_none()

    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment not found"
        )

    record = MaintenanceRecord(
        **maintenance_data.model_dump(),
        created_by=current_user.id
    )

    db.add(record)

    # Update equipment status if needed
    if maintenance_data.status == "in_progress":
        equipment.status = "maintenance"

    await db.commit()
    await db.refresh(record)

    return MaintenanceResponse.model_validate(record)


@router.get("/stats")
async def get_maintenance_stats(
    db: DB,
    current_user: CurrentUser,
):
    """Get maintenance statistics"""
    from datetime import timedelta
    today = date.today()

    # Count by status
    pending_result = await db.execute(
        select(func.count()).where(MaintenanceRecord.status == "pending")
    )
    pending = pending_result.scalar() or 0

    in_progress_result = await db.execute(
        select(func.count()).where(MaintenanceRecord.status == "in_progress")
    )
    in_progress = in_progress_result.scalar() or 0

    completed_result = await db.execute(
        select(func.count()).where(MaintenanceRecord.status == "completed")
    )
    completed = completed_result.scalar() or 0

    # Overdue
    overdue_result = await db.execute(
        select(func.count()).where(
            and_(
                MaintenanceRecord.status.in_(["pending", "in_progress"]),
                MaintenanceRecord.scheduled_date < today
            )
        )
    )
    overdue = overdue_result.scalar() or 0

    # Due in 7 days
    seven_days = today + timedelta(days=7)
    due_soon_result = await db.execute(
        select(func.count()).where(
            and_(
                MaintenanceRecord.status == "pending",
                MaintenanceRecord.scheduled_date <= seven_days,
                MaintenanceRecord.scheduled_date >= today
            )
        )
    )
    due_soon = due_soon_result.scalar() or 0

    return {
        "pending": pending,
        "in_progress": in_progress,
        "completed": completed,
        "overdue": overdue,
        "due_soon": due_soon,
        "total": pending + in_progress + completed
    }


@router.get("/upcoming", response_model=List[MaintenanceResponse])
async def get_upcoming_maintenance(
    db: DB,
    current_user: CurrentUser,
    days: int = Query(30, ge=1, le=365),
):
    """Get upcoming scheduled maintenance"""
    today = date.today()
    target_date = today + timedelta(days=days)

    from datetime import timedelta

    result = await db.execute(
        select(MaintenanceRecord)
        .options(
            selectinload(MaintenanceRecord.equipment),
            selectinload(MaintenanceRecord.assignee)
        )
        .where(
            and_(
                MaintenanceRecord.status == "pending",
                MaintenanceRecord.scheduled_date <= target_date,
                MaintenanceRecord.scheduled_date >= today
            )
        )
        .order_by(MaintenanceRecord.scheduled_date)
    )
    records = result.scalars().all()

    return [MaintenanceResponse.model_validate(r) for r in records]


@router.get("/overdue", response_model=List[MaintenanceResponse])
async def get_overdue_maintenance(
    db: DB,
    current_user: LeaderUser,
):
    """Get overdue maintenance"""
    today = date.today()

    result = await db.execute(
        select(MaintenanceRecord)
        .options(
            selectinload(MaintenanceRecord.equipment),
            selectinload(MaintenanceRecord.assignee)
        )
        .where(
            and_(
                MaintenanceRecord.status.in_(["pending", "in_progress"]),
                MaintenanceRecord.scheduled_date < today
            )
        )
        .order_by(MaintenanceRecord.scheduled_date)
    )
    records = result.scalars().all()

    return [MaintenanceResponse.model_validate(r) for r in records]


@router.get("/{maintenance_id}", response_model=MaintenanceResponse)
async def get_maintenance(
    maintenance_id: UUID,
    db: DB,
    current_user: CurrentUser,
):
    """Get maintenance record"""
    result = await db.execute(
        select(MaintenanceRecord)
        .options(
            selectinload(MaintenanceRecord.equipment),
            selectinload(MaintenanceRecord.performer),
            selectinload(MaintenanceRecord.assignee)
        )
        .where(MaintenanceRecord.id == maintenance_id)
    )
    record = result.scalar_one_or_none()

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Maintenance record not found"
        )

    return MaintenanceResponse.model_validate(record)


@router.put("/{maintenance_id}", response_model=MaintenanceResponse)
async def update_maintenance(
    maintenance_id: UUID,
    maintenance_data: MaintenanceUpdate,
    db: DB,
    current_user: ManagerUser,
):
    """Update maintenance record"""
    result = await db.execute(
        select(MaintenanceRecord)
        .options(selectinload(MaintenanceRecord.equipment))
        .where(MaintenanceRecord.id == maintenance_id)
    )
    record = result.scalar_one_or_none()

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Maintenance record not found"
        )

    update_data = maintenance_data.model_dump(exclude_unset=True)

    # Handle status change
    if "status" in update_data:
        if update_data["status"] == "in_progress":
            record.started_at = datetime.utcnow()
            record.equipment.status = "maintenance"
        elif update_data["status"] == "completed":
            record.completed_at = datetime.utcnow()
            record.performed_by = current_user.id
            record.equipment.status = "available"
            record.equipment.last_maintenance_date = date.today()
        elif update_data["status"] == "cancelled":
            if record.equipment.status == "maintenance":
                record.equipment.status = "available"

    for field, value in update_data.items():
        setattr(record, field, value)

    await db.commit()
    await db.refresh(record)

    return MaintenanceResponse.model_validate(record)


@router.put("/{maintenance_id}/complete", response_model=MaintenanceResponse)
async def complete_maintenance(
    maintenance_id: UUID,
    completion: MaintenanceComplete,
    db: DB,
    current_user: ManagerUser,
):
    """Complete maintenance"""
    result = await db.execute(
        select(MaintenanceRecord)
        .options(selectinload(MaintenanceRecord.equipment))
        .where(MaintenanceRecord.id == maintenance_id)
    )
    record = result.scalar_one_or_none()

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Maintenance record not found"
        )

    record.status = "completed"
    record.completed_at = datetime.utcnow()
    record.performed_by = current_user.id
    record.cost = completion.cost
    record.next_maintenance_date = completion.next_maintenance_date
    record.notes = completion.notes

    # Update equipment
    record.equipment.status = "available"
    record.equipment.last_maintenance_date = date.today()
    if completion.next_maintenance_date:
        record.equipment.next_maintenance_date = completion.next_maintenance_date

    await db.commit()
    await db.refresh(record)

    return MaintenanceResponse.model_validate(record)
