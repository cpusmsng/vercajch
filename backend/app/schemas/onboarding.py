from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel


class OnboardingStart(BaseModel):
    pass


class OnboardingSession(BaseModel):
    session_id: UUID
    expires_at: datetime
    steps: List[str] = ["scan", "photos", "details", "accessories", "calibration", "summary"]


class OnboardingScan(BaseModel):
    tag_type: str  # qr_code, barcode, rfid_nfc, rfid_uhf, manual
    tag_value: str
    rfid_uid: Optional[str] = None
    manual_code: Optional[str] = None


class OnboardingScanResponse(BaseModel):
    tag_id: UUID
    is_new_tag: bool
    existing_equipment: Optional[dict] = None


class OnboardingPhotoUpload(BaseModel):
    photo_type: str  # main, detail, label, damage
    description: Optional[str] = None


class OnboardingPhotoResponse(BaseModel):
    photo_id: UUID
    url: str
    thumbnail_url: Optional[str] = None


class OnboardingDetails(BaseModel):
    name: str
    category_id: UUID
    manufacturer_id: Optional[UUID] = None
    manufacturer_name: Optional[str] = None  # For creating new
    model_id: Optional[UUID] = None
    model_name: Optional[str] = None  # For creating new
    serial_number: Optional[str] = None
    internal_code: Optional[str] = None
    purchase_date: Optional[date] = None
    purchase_price: Optional[Decimal] = None
    warranty_expiry: Optional[date] = None
    notes: Optional[str] = None
    custom_fields: Optional[dict] = None


class OnboardingAccessoryItem(BaseModel):
    name: str
    accessory_type_id: Optional[UUID] = None
    tag_value: Optional[str] = None
    serial_number: Optional[str] = None
    quantity: int = 1


class OnboardingAccessory(BaseModel):
    accessories: List[OnboardingAccessoryItem]


class OnboardingCalibrationData(BaseModel):
    calibration_date: date
    valid_until: date
    certificate_number: Optional[str] = None
    performed_by_name: Optional[str] = None
    calibration_lab: Optional[str] = None


class OnboardingCalibration(BaseModel):
    requires_calibration: bool
    calibration_interval_days: Optional[int] = None
    initial_calibration: Optional[OnboardingCalibrationData] = None


class OnboardingComplete(BaseModel):
    initial_location_id: UUID
    initial_holder_id: Optional[UUID] = None


class OnboardingCompleteResponse(BaseModel):
    equipment_id: UUID
    accessories: List[dict] = []
    tag_id: UUID
