from typing import Optional
from uuid import UUID

from fastapi import APIRouter

from app.api.deps import DB, CurrentUser, ManagerUser
from app.core.config import settings as app_settings

router = APIRouter()


@router.get("")
async def get_settings(
    db: DB,
    current_user: CurrentUser,
):
    """Get application settings for the current user"""
    return {
        "app_name": app_settings.APP_NAME,
        "app_version": app_settings.APP_VERSION,
        "features": {
            "calibration_tracking": True,
            "maintenance_tracking": True,
            "transfer_workflow": True,
            "qr_code_scanning": True,
            "rfid_scanning": True,
            "photo_documentation": True,
            "offline_mode": True,
        },
        "limits": {
            "max_upload_size_mb": app_settings.MAX_UPLOAD_SIZE // (1024 * 1024),
            "max_photos_per_equipment": 10,
        },
        "user": {
            "id": str(current_user.id),
            "email": current_user.email,
            "full_name": current_user.full_name,
            "can_access_web": current_user.can_access_web,
            "can_access_mobile": current_user.can_access_mobile,
        },
    }


@router.get("/public")
async def get_public_settings():
    """Get public application settings (no auth required)"""
    return {
        "app_name": app_settings.APP_NAME,
        "app_version": app_settings.APP_VERSION,
        "qr_base_url": app_settings.QR_BASE_URL,
    }
