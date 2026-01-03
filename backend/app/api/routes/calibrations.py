from datetime import date, timedelta
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, status, Query, UploadFile, File
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload

from app.api.deps import DB, CurrentUser, LeaderUser, ManagerUser
from app.models.calibration import Calibration, CalibrationReminderSetting
from app.models.equipment import Equipment
from app.schemas.calibration import (
    CalibrationCreate,
    CalibrationUpdate,
    CalibrationResponse,
    CalibrationDashboard,
    CalibrationSummary,
    CalibrationDueItem,
    CalibrationReminderSettingCreate,
    CalibrationReminderSettingResponse,
)
from app.schemas.equipment import EquipmentListResponse

router = APIRouter()


@router.get("/dashboard", response_model=CalibrationDashboard)
async def get_calibration_dashboard(
    db: DB,
    current_user: CurrentUser,
    category_id: Optional[UUID] = None,
    department_id: Optional[UUID] = None,
):
    """Get calibration dashboard with statistics"""
    today = date.today()
    thirty_days = today + timedelta(days=30)
    seven_days = today + timedelta(days=7)

    # Base query for equipment requiring calibration
    base_query = select(Equipment).where(Equipment.requires_calibration == True)

    if category_id:
        base_query = base_query.where(Equipment.category_id == category_id)

    # Count total
    total_result = await db.execute(
        select(func.count()).select_from(base_query.subquery())
    )
    total = total_result.scalar() or 0

    # Count valid (next_calibration_date > 30 days)
    valid_result = await db.execute(
        select(func.count()).where(
            and_(
                Equipment.requires_calibration == True,
                Equipment.next_calibration_date > thirty_days
            )
        )
    )
    valid = valid_result.scalar() or 0

    # Count expiring in 30 days
    expiring_30_result = await db.execute(
        select(func.count()).where(
            and_(
                Equipment.requires_calibration == True,
                Equipment.next_calibration_date <= thirty_days,
                Equipment.next_calibration_date > seven_days
            )
        )
    )
    expiring_30 = expiring_30_result.scalar() or 0

    # Count expiring in 7 days
    expiring_7_result = await db.execute(
        select(func.count()).where(
            and_(
                Equipment.requires_calibration == True,
                Equipment.next_calibration_date <= seven_days,
                Equipment.next_calibration_date > today
            )
        )
    )
    expiring_7 = expiring_7_result.scalar() or 0

    # Count expired
    expired_result = await db.execute(
        select(func.count()).where(
            and_(
                Equipment.requires_calibration == True,
                Equipment.next_calibration_date <= today
            )
        )
    )
    expired = expired_result.scalar() or 0

    # Get upcoming (next 30 days)
    upcoming_result = await db.execute(
        select(Equipment)
        .options(
            selectinload(Equipment.category),
            selectinload(Equipment.current_location),
            selectinload(Equipment.current_holder)
        )
        .where(
            and_(
                Equipment.requires_calibration == True,
                Equipment.next_calibration_date <= thirty_days,
                Equipment.next_calibration_date > today
            )
        )
        .order_by(Equipment.next_calibration_date)
        .limit(20)
    )
    upcoming_equipment = upcoming_result.scalars().all()

    upcoming = []
    for eq in upcoming_equipment:
        days = (eq.next_calibration_date - today).days if eq.next_calibration_date else 0
        upcoming.append(CalibrationDueItem(
            equipment=EquipmentListResponse.model_validate(eq),
            days_until_expiry=days,
            last_calibration=None
        ))

    # Get expired
    expired_result = await db.execute(
        select(Equipment)
        .options(
            selectinload(Equipment.category),
            selectinload(Equipment.current_location),
            selectinload(Equipment.current_holder)
        )
        .where(
            and_(
                Equipment.requires_calibration == True,
                Equipment.next_calibration_date <= today
            )
        )
        .order_by(Equipment.next_calibration_date)
        .limit(20)
    )
    expired_equipment = expired_result.scalars().all()

    expired_list = []
    for eq in expired_equipment:
        days = (today - eq.next_calibration_date).days if eq.next_calibration_date else 0
        expired_list.append(CalibrationDueItem(
            equipment=EquipmentListResponse.model_validate(eq),
            days_until_expiry=-days,
            last_calibration=None
        ))

    return CalibrationDashboard(
        summary=CalibrationSummary(
            total_requiring_calibration=total,
            valid=valid,
            expiring_30_days=expiring_30,
            expiring_7_days=expiring_7,
            expired=expired
        ),
        upcoming=upcoming,
        expired=expired_list
    )


@router.get("/due")
async def get_calibrations_due(
    db: DB,
    current_user: CurrentUser,
    status: Optional[str] = None,  # expiring, expired, all
    days_ahead: int = Query(30, ge=1, le=365),
    category_id: Optional[UUID] = None,
):
    """Get equipment due for calibration"""
    today = date.today()
    target_date = today + timedelta(days=days_ahead)

    query = select(Equipment).options(
        selectinload(Equipment.category),
        selectinload(Equipment.current_location),
        selectinload(Equipment.current_holder)
    ).where(Equipment.requires_calibration == True)

    if category_id:
        query = query.where(Equipment.category_id == category_id)

    if status == "expiring":
        query = query.where(
            and_(
                Equipment.next_calibration_date <= target_date,
                Equipment.next_calibration_date > today
            )
        )
    elif status == "expired":
        query = query.where(Equipment.next_calibration_date <= today)
    else:
        query = query.where(Equipment.next_calibration_date <= target_date)

    query = query.order_by(Equipment.next_calibration_date)
    result = await db.execute(query)
    equipment = result.scalars().all()

    items = []
    for eq in equipment:
        days = (eq.next_calibration_date - today).days if eq.next_calibration_date else 0
        items.append({
            "equipment": EquipmentListResponse.model_validate(eq),
            "days_until_expiry": days,
            "status": "expired" if days < 0 else ("expiring" if days <= 7 else "valid")
        })

    return items


# Equipment calibrations
@router.get("/equipment/new")
async def get_new_equipment_calibrations(
    db: DB,
    current_user: CurrentUser,
):
    """Get calibrations for new equipment (empty list)"""
    return []


@router.get("/equipment/{equipment_id}", response_model=List[CalibrationResponse])
async def get_equipment_calibrations(
    equipment_id: UUID,
    db: DB,
    current_user: CurrentUser,
):
    """Get calibration history for equipment"""
    result = await db.execute(
        select(Calibration)
        .where(Calibration.equipment_id == equipment_id)
        .order_by(Calibration.calibration_date.desc())
    )
    calibrations = result.scalars().all()

    today = date.today()
    response = []
    for cal in calibrations:
        days = (cal.valid_until - today).days if cal.valid_until else 0
        status = "expired" if days < 0 else ("expiring" if days <= 30 else "valid")

        cal_response = CalibrationResponse.model_validate(cal)
        cal_response.days_until_expiry = days
        cal_response.status = status
        response.append(cal_response)

    return response


@router.post("/equipment/{equipment_id}", response_model=CalibrationResponse, status_code=status.HTTP_201_CREATED)
async def create_calibration(
    equipment_id: UUID,
    calibration_data: CalibrationCreate,
    db: DB,
    current_user: LeaderUser,
):
    """Add a new calibration record"""
    # Check equipment exists
    eq_result = await db.execute(
        select(Equipment).where(Equipment.id == equipment_id)
    )
    equipment = eq_result.scalar_one_or_none()

    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment not found"
        )

    calibration = Calibration(
        equipment_id=equipment_id,
        **calibration_data.model_dump(),
        recorded_by=current_user.id
    )

    db.add(calibration)

    # Update equipment calibration info
    equipment.last_calibration_date = calibration_data.calibration_date
    equipment.next_calibration_date = calibration_data.valid_until

    today = date.today()
    days_until = (calibration_data.valid_until - today).days
    if days_until < 0:
        equipment.calibration_status = "expired"
    elif days_until <= 30:
        equipment.calibration_status = "expiring"
    else:
        equipment.calibration_status = "valid"

    await db.commit()
    await db.refresh(calibration)

    return CalibrationResponse.model_validate(calibration)


@router.put("/{calibration_id}", response_model=CalibrationResponse)
async def update_calibration(
    calibration_id: UUID,
    calibration_data: CalibrationUpdate,
    db: DB,
    current_user: ManagerUser,
):
    """Update a calibration record"""
    result = await db.execute(
        select(Calibration).where(Calibration.id == calibration_id)
    )
    calibration = result.scalar_one_or_none()

    if not calibration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calibration not found"
        )

    update_data = calibration_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(calibration, field, value)

    await db.commit()
    await db.refresh(calibration)

    return CalibrationResponse.model_validate(calibration)


@router.post("/{calibration_id}/certificate")
async def upload_certificate(
    calibration_id: UUID,
    file: UploadFile = File(...),
    db: DB = None,
    current_user: LeaderUser = None,
):
    """Upload calibration certificate"""
    result = await db.execute(
        select(Calibration).where(Calibration.id == calibration_id)
    )
    calibration = result.scalar_one_or_none()

    if not calibration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calibration not found"
        )

    # TODO: Upload to MinIO/S3
    certificate_url = f"/uploads/calibrations/{calibration_id}/{file.filename}"
    calibration.certificate_url = certificate_url

    await db.commit()

    return {"certificate_url": certificate_url}


# Reminder settings
@router.get("/reminder-settings", response_model=List[CalibrationReminderSettingResponse])
async def get_reminder_settings(
    db: DB,
    current_user: ManagerUser,
):
    """Get calibration reminder settings"""
    result = await db.execute(
        select(CalibrationReminderSetting).order_by(CalibrationReminderSetting.scope_type)
    )
    settings = result.scalars().all()

    return [CalibrationReminderSettingResponse.model_validate(s) for s in settings]


@router.post("/reminder-settings", response_model=CalibrationReminderSettingResponse)
async def create_reminder_setting(
    setting_data: CalibrationReminderSettingCreate,
    db: DB,
    current_user: ManagerUser,
):
    """Create calibration reminder setting"""
    setting = CalibrationReminderSetting(
        **setting_data.model_dump(),
        created_by=current_user.id
    )

    db.add(setting)
    await db.commit()
    await db.refresh(setting)

    return CalibrationReminderSettingResponse.model_validate(setting)
