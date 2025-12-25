from datetime import datetime
from typing import List
from uuid import UUID

from fastapi import APIRouter, HTTPException, status, Query
from sqlalchemy import select, func

from app.api.deps import DB, CurrentUser
from app.models.notification import Notification
from app.schemas.notification import NotificationResponse
from app.schemas.common import PaginatedResponse

router = APIRouter()


@router.get("", response_model=PaginatedResponse[NotificationResponse])
async def list_notifications(
    db: DB,
    current_user: CurrentUser,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    unread_only: bool = False,
):
    """Get user's notifications"""
    query = select(Notification).where(Notification.user_id == current_user.id)

    if unread_only:
        query = query.where(Notification.is_read == False)

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    # Paginate
    query = query.offset((page - 1) * size).limit(size).order_by(Notification.created_at.desc())
    result = await db.execute(query)
    notifications = result.scalars().all()

    return PaginatedResponse(
        items=[NotificationResponse.model_validate(n) for n in notifications],
        total=total,
        page=page,
        size=size,
        pages=(total + size - 1) // size
    )


@router.get("/unread-count")
async def get_unread_count(
    db: DB,
    current_user: CurrentUser,
):
    """Get unread notification count"""
    result = await db.execute(
        select(func.count())
        .where(
            Notification.user_id == current_user.id,
            Notification.is_read == False
        )
    )
    count = result.scalar() or 0

    return {"unread_count": count}


@router.put("/{notification_id}/read")
async def mark_as_read(
    notification_id: UUID,
    db: DB,
    current_user: CurrentUser,
):
    """Mark notification as read"""
    result = await db.execute(
        select(Notification).where(
            Notification.id == notification_id,
            Notification.user_id == current_user.id
        )
    )
    notification = result.scalar_one_or_none()

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )

    notification.is_read = True
    notification.read_at = datetime.utcnow()

    await db.commit()

    return {"message": "Notification marked as read"}


@router.put("/read-all")
async def mark_all_as_read(
    db: DB,
    current_user: CurrentUser,
):
    """Mark all notifications as read"""
    result = await db.execute(
        select(Notification).where(
            Notification.user_id == current_user.id,
            Notification.is_read == False
        )
    )
    notifications = result.scalars().all()

    now = datetime.utcnow()
    for notification in notifications:
        notification.is_read = True
        notification.read_at = now

    await db.commit()

    return {"message": f"{len(notifications)} notifications marked as read"}


@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: UUID,
    db: DB,
    current_user: CurrentUser,
):
    """Delete notification"""
    result = await db.execute(
        select(Notification).where(
            Notification.id == notification_id,
            Notification.user_id == current_user.id
        )
    )
    notification = result.scalar_one_or_none()

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )

    await db.delete(notification)
    await db.commit()

    return {"message": "Notification deleted"}
