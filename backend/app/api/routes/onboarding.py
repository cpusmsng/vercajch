import uuid as uuid_module
from datetime import datetime, timedelta, date
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, status, UploadFile, File, Form
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.api.deps import DB, ManagerUser
from app.core.config import settings
from app.models.equipment import Equipment, EquipmentTag, EquipmentPhoto, Category, Manufacturer, EquipmentModel
from app.models.calibration import Calibration
from app.schemas.onboarding import (
    OnboardingStart,
    OnboardingSession,
    OnboardingScan,
    OnboardingScanResponse,
    OnboardingPhotoResponse,
    OnboardingDetails,
    OnboardingAccessory,
    OnboardingCalibration,
    OnboardingComplete,
    OnboardingCompleteResponse,
)

router = APIRouter()

# In-memory session storage (in production, use Redis)
onboarding_sessions = {}


@router.post("/start", response_model=OnboardingSession)
async def start_onboarding(
    db: DB,
    current_user: ManagerUser,
):
    """Start a new onboarding session"""
    session_id = uuid_module.uuid4()
    expires_at = datetime.utcnow() + timedelta(hours=2)

    onboarding_sessions[str(session_id)] = {
        "user_id": str(current_user.id),
        "created_at": datetime.utcnow(),
        "expires_at": expires_at,
        "tag": None,
        "photos": [],
        "details": None,
        "accessories": [],
        "calibration": None,
    }

    return OnboardingSession(
        session_id=session_id,
        expires_at=expires_at,
        steps=["scan", "photos", "details", "accessories", "calibration", "summary"]
    )


@router.post("/{session_id}/scan", response_model=OnboardingScanResponse)
async def scan_tag(
    session_id: UUID,
    scan_data: OnboardingScan,
    db: DB,
    current_user: ManagerUser,
):
    """Step 1: Scan or register a tag"""
    session = onboarding_sessions.get(str(session_id))
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found or expired"
        )

    # Check if tag already exists
    result = await db.execute(
        select(EquipmentTag)
        .options(selectinload(EquipmentTag.equipment))
        .where(EquipmentTag.tag_value == scan_data.tag_value)
    )
    existing_tag = result.scalar_one_or_none()

    if existing_tag and existing_tag.equipment:
        # Tag already assigned to equipment
        return OnboardingScanResponse(
            tag_id=existing_tag.id,
            is_new_tag=False,
            existing_equipment={
                "id": str(existing_tag.equipment.id),
                "name": existing_tag.equipment.name,
                "internal_code": existing_tag.equipment.internal_code
            }
        )

    # Create or update tag
    if existing_tag:
        tag = existing_tag
    else:
        tag = EquipmentTag(
            tag_type=scan_data.tag_type,
            tag_value=scan_data.tag_value,
            rfid_uid=scan_data.rfid_uid,
            created_by=current_user.id
        )
        db.add(tag)
        await db.commit()
        await db.refresh(tag)

    # Store in session
    session["tag"] = {
        "id": str(tag.id),
        "tag_type": scan_data.tag_type,
        "tag_value": scan_data.tag_value,
        "rfid_uid": scan_data.rfid_uid
    }

    return OnboardingScanResponse(
        tag_id=tag.id,
        is_new_tag=True,
        existing_equipment=None
    )


@router.post("/{session_id}/photos", response_model=OnboardingPhotoResponse)
async def upload_photo(
    session_id: UUID,
    photo_type: str = Form(...),
    description: Optional[str] = Form(None),
    file: UploadFile = File(...),
    db: DB = None,
    current_user: ManagerUser = None,
):
    """Step 2: Upload equipment photos"""
    session = onboarding_sessions.get(str(session_id))
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found or expired"
        )

    # TODO: Upload to MinIO/S3
    photo_id = uuid_module.uuid4()
    file_url = f"/uploads/onboarding/{session_id}/{photo_id}_{file.filename}"
    thumbnail_url = f"/uploads/onboarding/{session_id}/thumb_{photo_id}_{file.filename}"

    session["photos"].append({
        "id": str(photo_id),
        "photo_type": photo_type,
        "file_url": file_url,
        "thumbnail_url": thumbnail_url,
        "description": description
    })

    return OnboardingPhotoResponse(
        photo_id=photo_id,
        url=file_url,
        thumbnail_url=thumbnail_url
    )


@router.post("/{session_id}/details")
async def set_details(
    session_id: UUID,
    details: OnboardingDetails,
    db: DB,
    current_user: ManagerUser,
):
    """Step 3: Set equipment details"""
    session = onboarding_sessions.get(str(session_id))
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found or expired"
        )

    # Handle new manufacturer
    manufacturer_id = details.manufacturer_id
    if details.manufacturer_name and not manufacturer_id:
        manufacturer = Manufacturer(name=details.manufacturer_name)
        db.add(manufacturer)
        await db.commit()
        await db.refresh(manufacturer)
        manufacturer_id = manufacturer.id

    # Handle new model
    model_id = details.model_id
    if details.model_name and not model_id:
        model = EquipmentModel(
            name=details.model_name,
            manufacturer_id=manufacturer_id,
            category_id=details.category_id
        )
        db.add(model)
        await db.commit()
        await db.refresh(model)
        model_id = model.id

    session["details"] = {
        "name": details.name,
        "category_id": str(details.category_id),
        "manufacturer_id": str(manufacturer_id) if manufacturer_id else None,
        "model_id": str(model_id) if model_id else None,
        "serial_number": details.serial_number,
        "internal_code": details.internal_code,
        "purchase_date": details.purchase_date.isoformat() if details.purchase_date else None,
        "purchase_price": float(details.purchase_price) if details.purchase_price else None,
        "warranty_expiry": details.warranty_expiry.isoformat() if details.warranty_expiry else None,
        "notes": details.notes,
        "custom_fields": details.custom_fields
    }

    return {"message": "Details saved"}


@router.post("/{session_id}/accessories")
async def set_accessories(
    session_id: UUID,
    accessories: OnboardingAccessory,
    db: DB,
    current_user: ManagerUser,
):
    """Step 4: Add accessories"""
    session = onboarding_sessions.get(str(session_id))
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found or expired"
        )

    session["accessories"] = [
        {
            "name": acc.name,
            "accessory_type_id": str(acc.accessory_type_id) if acc.accessory_type_id else None,
            "tag_value": acc.tag_value,
            "serial_number": acc.serial_number,
            "quantity": acc.quantity
        }
        for acc in accessories.accessories
    ]

    return {"message": "Accessories saved"}


@router.post("/{session_id}/calibration")
async def set_calibration(
    session_id: UUID,
    calibration: OnboardingCalibration,
    db: DB,
    current_user: ManagerUser,
):
    """Step 5: Set calibration info"""
    session = onboarding_sessions.get(str(session_id))
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found or expired"
        )

    session["calibration"] = {
        "requires_calibration": calibration.requires_calibration,
        "calibration_interval_days": calibration.calibration_interval_days,
        "initial_calibration": {
            "calibration_date": calibration.initial_calibration.calibration_date.isoformat(),
            "valid_until": calibration.initial_calibration.valid_until.isoformat(),
            "certificate_number": calibration.initial_calibration.certificate_number,
            "performed_by_name": calibration.initial_calibration.performed_by_name,
            "calibration_lab": calibration.initial_calibration.calibration_lab
        } if calibration.initial_calibration else None
    }

    return {"message": "Calibration info saved"}


@router.post("/{session_id}/complete", response_model=OnboardingCompleteResponse)
async def complete_onboarding(
    session_id: UUID,
    completion: OnboardingComplete,
    db: DB,
    current_user: ManagerUser,
):
    """Complete onboarding and create equipment"""
    session = onboarding_sessions.get(str(session_id))
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found or expired"
        )

    details = session.get("details")
    if not details:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Details not provided"
        )

    # Check internal_code uniqueness
    if details.get("internal_code"):
        existing = await db.execute(
            select(Equipment).where(Equipment.internal_code == details["internal_code"])
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Internal code already exists"
            )

    # Get main photo
    main_photo = next(
        (p for p in session.get("photos", []) if p["photo_type"] == "main"),
        session.get("photos", [{}])[0] if session.get("photos") else None
    )

    # Create equipment
    calibration_data = session.get("calibration", {})
    equipment = Equipment(
        name=details["name"],
        category_id=UUID(details["category_id"]),
        model_id=UUID(details["model_id"]) if details.get("model_id") else None,
        serial_number=details.get("serial_number"),
        internal_code=details.get("internal_code"),
        purchase_date=date.fromisoformat(details["purchase_date"]) if details.get("purchase_date") else None,
        purchase_price=details.get("purchase_price"),
        warranty_expiry=date.fromisoformat(details["warranty_expiry"]) if details.get("warranty_expiry") else None,
        notes=details.get("notes"),
        custom_fields=details.get("custom_fields"),
        photo_url=main_photo.get("file_url") if main_photo else None,
        current_location_id=completion.initial_location_id,
        current_holder_id=completion.initial_holder_id,
        home_location_id=completion.initial_location_id,
        status="available" if not completion.initial_holder_id else "checked_out",
        requires_calibration=calibration_data.get("requires_calibration", False),
        calibration_interval_days=calibration_data.get("calibration_interval_days"),
    )

    # Set calibration dates
    if calibration_data.get("initial_calibration"):
        cal = calibration_data["initial_calibration"]
        equipment.last_calibration_date = date.fromisoformat(cal["calibration_date"])
        equipment.next_calibration_date = date.fromisoformat(cal["valid_until"])

        today = date.today()
        days_until = (equipment.next_calibration_date - today).days
        equipment.calibration_status = "expired" if days_until < 0 else ("expiring" if days_until <= 30 else "valid")

    db.add(equipment)
    await db.flush()

    # Link tag to equipment
    tag_data = session.get("tag")
    if tag_data:
        tag_result = await db.execute(
            select(EquipmentTag).where(EquipmentTag.id == UUID(tag_data["id"]))
        )
        tag = tag_result.scalar_one_or_none()
        if tag:
            tag.equipment_id = equipment.id
            tag.applied_at = datetime.utcnow()

    # Create photos
    for photo_data in session.get("photos", []):
        photo = EquipmentPhoto(
            equipment_id=equipment.id,
            photo_type=photo_data["photo_type"],
            file_url=photo_data["file_url"],
            thumbnail_url=photo_data.get("thumbnail_url"),
            description=photo_data.get("description"),
            uploaded_by=current_user.id,
            is_synced=True
        )
        db.add(photo)

    # Create accessories
    accessories_created = []
    for acc_data in session.get("accessories", []):
        for i in range(acc_data.get("quantity", 1)):
            accessory = Equipment(
                name=acc_data["name"] + (f" ({i+1})" if acc_data.get("quantity", 1) > 1 else ""),
                category_id=equipment.category_id,
                serial_number=acc_data.get("serial_number"),
                parent_equipment_id=equipment.id,
                is_main_item=False,
                current_location_id=equipment.current_location_id,
                current_holder_id=equipment.current_holder_id,
                status=equipment.status
            )
            db.add(accessory)
            await db.flush()

            # Create tag for accessory if provided
            if acc_data.get("tag_value"):
                acc_tag = EquipmentTag(
                    equipment_id=accessory.id,
                    tag_type="qr_code",
                    tag_value=acc_data["tag_value"],
                    created_by=current_user.id,
                    applied_at=datetime.utcnow()
                )
                db.add(acc_tag)

            accessories_created.append({
                "id": str(accessory.id),
                "name": accessory.name
            })

    # Create initial calibration record
    if calibration_data.get("initial_calibration"):
        cal = calibration_data["initial_calibration"]
        calibration_record = Calibration(
            equipment_id=equipment.id,
            calibration_type="initial",
            calibration_date=date.fromisoformat(cal["calibration_date"]),
            valid_until=date.fromisoformat(cal["valid_until"]),
            performed_by_name=cal.get("performed_by_name"),
            calibration_lab=cal.get("calibration_lab"),
            certificate_number=cal.get("certificate_number"),
            result="passed",
            recorded_by=current_user.id
        )
        db.add(calibration_record)

    await db.commit()

    # Clean up session
    del onboarding_sessions[str(session_id)]

    return OnboardingCompleteResponse(
        equipment_id=equipment.id,
        accessories=accessories_created,
        tag_id=UUID(tag_data["id"]) if tag_data else equipment.id
    )
