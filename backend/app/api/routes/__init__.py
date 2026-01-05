from fastapi import APIRouter

from .auth import router as auth_router
from .users import router as users_router
from .equipment import router as equipment_router
from .categories import router as categories_router
from .locations import router as locations_router
from .manufacturers import router as manufacturers_router
from .calibrations import router as calibrations_router
from .checkouts import router as checkouts_router
from .transfers import router as transfers_router
from .onboarding import router as onboarding_router
from .tags import router as tags_router
from .maintenance import router as maintenance_router
from .notifications import router as notifications_router
from .reports import router as reports_router
from .settings import router as settings_router
from .websocket import router as websocket_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users_router, prefix="/users", tags=["Users"])
api_router.include_router(equipment_router, prefix="/equipment", tags=["Equipment"])
api_router.include_router(categories_router, prefix="/categories", tags=["Categories"])
api_router.include_router(locations_router, prefix="/locations", tags=["Locations"])
api_router.include_router(manufacturers_router, prefix="/manufacturers", tags=["Manufacturers"])
api_router.include_router(calibrations_router, prefix="/calibrations", tags=["Calibrations"])
api_router.include_router(checkouts_router, prefix="/checkouts", tags=["Checkouts"])
api_router.include_router(transfers_router, prefix="/transfers", tags=["Transfers"])
api_router.include_router(onboarding_router, prefix="/onboarding", tags=["Onboarding"])
api_router.include_router(tags_router, prefix="/tags", tags=["Tags"])
api_router.include_router(maintenance_router, prefix="/maintenance", tags=["Maintenance"])
api_router.include_router(notifications_router, prefix="/notifications", tags=["Notifications"])
api_router.include_router(reports_router, prefix="/reports", tags=["Reports"])
api_router.include_router(settings_router, prefix="/settings", tags=["Settings"])
api_router.include_router(websocket_router, tags=["WebSocket"])
