from datetime import date, timedelta
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Query
from sqlalchemy import select, func, and_

from app.api.deps import DB, CurrentUser, LeaderUser, ManagerUser
from app.models.equipment import Equipment, Category
from app.models.checkout import Checkout
from app.models.maintenance import MaintenanceRecord
from app.models.user import User

router = APIRouter()


@router.get("/equipment-summary")
async def get_equipment_summary(
    db: DB,
    current_user: CurrentUser,
    category_id: Optional[UUID] = None,
    location_id: Optional[UUID] = None,
):
    """Get equipment summary statistics"""
    base_query = select(Equipment).where(Equipment.is_main_item == True)

    if category_id:
        base_query = base_query.where(Equipment.category_id == category_id)
    if location_id:
        base_query = base_query.where(Equipment.current_location_id == location_id)

    # Total count
    total_result = await db.execute(
        select(func.count()).select_from(base_query.subquery())
    )
    total = total_result.scalar() or 0

    # By status
    status_result = await db.execute(
        select(Equipment.status, func.count())
        .where(Equipment.is_main_item == True)
        .group_by(Equipment.status)
    )
    by_status = {row[0]: row[1] for row in status_result.fetchall()}

    # By condition
    condition_result = await db.execute(
        select(Equipment.condition, func.count())
        .where(Equipment.is_main_item == True)
        .group_by(Equipment.condition)
    )
    by_condition = {row[0]: row[1] for row in condition_result.fetchall()}

    # By category
    category_result = await db.execute(
        select(Category.name, func.count())
        .join(Equipment, Equipment.category_id == Category.id)
        .where(Equipment.is_main_item == True)
        .group_by(Category.name)
    )
    by_category = {row[0]: row[1] for row in category_result.fetchall()}

    return {
        "total": total,
        "by_status": by_status,
        "by_condition": by_condition,
        "by_category": by_category
    }


@router.get("/checkout-stats")
async def get_checkout_stats(
    db: DB,
    current_user: LeaderUser,
    days: int = Query(30, ge=1, le=365),
):
    """Get checkout statistics"""
    start_date = date.today() - timedelta(days=days)

    # Total checkouts in period
    total_result = await db.execute(
        select(func.count()).where(
            Checkout.checkout_at >= start_date
        )
    )
    total_checkouts = total_result.scalar() or 0

    # Active checkouts
    active_result = await db.execute(
        select(func.count()).where(Checkout.status == "active")
    )
    active = active_result.scalar() or 0

    # Overdue
    overdue_result = await db.execute(
        select(func.count()).where(
            and_(
                Checkout.status == "active",
                Checkout.expected_return_at < date.today()
            )
        )
    )
    overdue = overdue_result.scalar() or 0

    # Checkouts by day (last 30 days)
    daily_result = await db.execute(
        select(
            func.date(Checkout.checkout_at),
            func.count()
        )
        .where(Checkout.checkout_at >= start_date)
        .group_by(func.date(Checkout.checkout_at))
        .order_by(func.date(Checkout.checkout_at))
    )
    daily_checkouts = [{"date": str(row[0]), "count": row[1]} for row in daily_result.fetchall()]

    # Top checked out equipment
    top_equipment_result = await db.execute(
        select(Equipment.name, Equipment.internal_code, func.count())
        .join(Checkout, Checkout.equipment_id == Equipment.id)
        .where(Checkout.checkout_at >= start_date)
        .group_by(Equipment.id, Equipment.name, Equipment.internal_code)
        .order_by(func.count().desc())
        .limit(10)
    )
    top_equipment = [
        {"name": row[0], "code": row[1], "count": row[2]}
        for row in top_equipment_result.fetchall()
    ]

    return {
        "period_days": days,
        "total_checkouts": total_checkouts,
        "active_checkouts": active,
        "overdue_checkouts": overdue,
        "daily_checkouts": daily_checkouts,
        "top_equipment": top_equipment
    }


@router.get("/maintenance-stats")
async def get_maintenance_stats(
    db: DB,
    current_user: ManagerUser,
    days: int = Query(30, ge=1, le=365),
):
    """Get maintenance statistics"""
    start_date = date.today() - timedelta(days=days)

    # By status
    status_result = await db.execute(
        select(MaintenanceRecord.status, func.count())
        .group_by(MaintenanceRecord.status)
    )
    by_status = {row[0]: row[1] for row in status_result.fetchall()}

    # By type
    type_result = await db.execute(
        select(MaintenanceRecord.type, func.count())
        .group_by(MaintenanceRecord.type)
    )
    by_type = {row[0]: row[1] for row in type_result.fetchall()}

    # Completed in period
    completed_result = await db.execute(
        select(func.count()).where(
            and_(
                MaintenanceRecord.status == "completed",
                MaintenanceRecord.completed_at >= start_date
            )
        )
    )
    completed = completed_result.scalar() or 0

    # Total cost in period
    cost_result = await db.execute(
        select(func.sum(MaintenanceRecord.cost)).where(
            and_(
                MaintenanceRecord.status == "completed",
                MaintenanceRecord.completed_at >= start_date
            )
        )
    )
    total_cost = float(cost_result.scalar() or 0)

    return {
        "period_days": days,
        "by_status": by_status,
        "by_type": by_type,
        "completed_in_period": completed,
        "total_cost": total_cost
    }


@router.get("/user-activity")
async def get_user_activity(
    db: DB,
    current_user: ManagerUser,
    days: int = Query(30, ge=1, le=365),
):
    """Get user activity statistics"""
    start_date = date.today() - timedelta(days=days)

    # Top users by checkouts
    user_checkout_result = await db.execute(
        select(User.full_name, func.count())
        .join(Checkout, Checkout.user_id == User.id)
        .where(Checkout.checkout_at >= start_date)
        .group_by(User.id, User.full_name)
        .order_by(func.count().desc())
        .limit(10)
    )
    top_by_checkouts = [
        {"user": row[0], "count": row[1]}
        for row in user_checkout_result.fetchall()
    ]

    # Equipment per user (current)
    equipment_per_user_result = await db.execute(
        select(User.full_name, func.count())
        .join(Equipment, Equipment.current_holder_id == User.id)
        .where(Equipment.is_main_item == True)
        .group_by(User.id, User.full_name)
        .order_by(func.count().desc())
        .limit(10)
    )
    top_equipment_holders = [
        {"user": row[0], "count": row[1]}
        for row in equipment_per_user_result.fetchall()
    ]

    return {
        "period_days": days,
        "top_by_checkouts": top_by_checkouts,
        "top_equipment_holders": top_equipment_holders
    }


@router.get("/inventory-value")
async def get_inventory_value(
    db: DB,
    current_user: ManagerUser,
    category_id: Optional[UUID] = None,
):
    """Get inventory value report"""
    query = select(
        func.sum(Equipment.purchase_price),
        func.sum(Equipment.current_value),
        func.count()
    ).where(Equipment.is_main_item == True)

    if category_id:
        query = query.where(Equipment.category_id == category_id)

    result = await db.execute(query)
    row = result.fetchone()

    total_purchase = float(row[0] or 0)
    total_current = float(row[1] or 0)
    total_count = row[2] or 0

    # By category
    category_result = await db.execute(
        select(
            Category.name,
            func.sum(Equipment.purchase_price),
            func.sum(Equipment.current_value),
            func.count()
        )
        .join(Equipment, Equipment.category_id == Category.id)
        .where(Equipment.is_main_item == True)
        .group_by(Category.id, Category.name)
        .order_by(func.sum(Equipment.current_value).desc())
    )
    by_category = [
        {
            "category": row[0],
            "purchase_value": float(row[1] or 0),
            "current_value": float(row[2] or 0),
            "count": row[3]
        }
        for row in category_result.fetchall()
    ]

    return {
        "total_count": total_count,
        "total_purchase_value": total_purchase,
        "total_current_value": total_current,
        "depreciation": total_purchase - total_current,
        "by_category": by_category
    }
