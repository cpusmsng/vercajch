from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, status, Query
from sqlalchemy import select

from app.api.deps import DB, CurrentUser, ManagerUser
from app.models.equipment import Manufacturer, EquipmentModel
from app.schemas.manufacturer import (
    ManufacturerCreate,
    ManufacturerResponse,
    EquipmentModelCreate,
    EquipmentModelResponse,
)

router = APIRouter()


@router.get("", response_model=List[ManufacturerResponse])
async def list_manufacturers(
    db: DB,
    current_user: CurrentUser,
    search: Optional[str] = None,
    is_active: Optional[bool] = True,
):
    """List manufacturers"""
    query = select(Manufacturer)

    if search:
        query = query.where(Manufacturer.name.ilike(f"%{search}%"))
    if is_active is not None:
        query = query.where(Manufacturer.is_active == is_active)

    query = query.order_by(Manufacturer.name)
    result = await db.execute(query)
    manufacturers = result.scalars().all()

    return [ManufacturerResponse.model_validate(m) for m in manufacturers]


@router.post("", response_model=ManufacturerResponse, status_code=status.HTTP_201_CREATED)
async def create_manufacturer(
    manufacturer_data: ManufacturerCreate,
    db: DB,
    current_user: ManagerUser,
):
    """Create a new manufacturer"""
    manufacturer = Manufacturer(**manufacturer_data.model_dump())
    db.add(manufacturer)
    await db.commit()
    await db.refresh(manufacturer)

    return ManufacturerResponse.model_validate(manufacturer)


@router.get("/{manufacturer_id}", response_model=ManufacturerResponse)
async def get_manufacturer(
    manufacturer_id: UUID,
    db: DB,
    current_user: CurrentUser,
):
    """Get manufacturer by ID"""
    result = await db.execute(
        select(Manufacturer).where(Manufacturer.id == manufacturer_id)
    )
    manufacturer = result.scalar_one_or_none()

    if not manufacturer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Manufacturer not found"
        )

    return ManufacturerResponse.model_validate(manufacturer)


@router.get("/{manufacturer_id}/models", response_model=List[EquipmentModelResponse])
async def get_manufacturer_models(
    manufacturer_id: UUID,
    db: DB,
    current_user: CurrentUser,
    category_id: Optional[UUID] = None,
):
    """Get models for a manufacturer"""
    query = select(EquipmentModel).where(EquipmentModel.manufacturer_id == manufacturer_id)

    if category_id:
        query = query.where(EquipmentModel.category_id == category_id)

    query = query.order_by(EquipmentModel.name)
    result = await db.execute(query)
    models = result.scalars().all()

    return [EquipmentModelResponse.model_validate(m) for m in models]


# Models endpoints
@router.get("/models", response_model=List[EquipmentModelResponse])
async def list_models(
    db: DB,
    current_user: CurrentUser,
    category_id: Optional[UUID] = None,
    manufacturer_id: Optional[UUID] = None,
    is_active: Optional[bool] = True,
):
    """List equipment models"""
    query = select(EquipmentModel)

    if category_id:
        query = query.where(EquipmentModel.category_id == category_id)
    if manufacturer_id:
        query = query.where(EquipmentModel.manufacturer_id == manufacturer_id)
    if is_active is not None:
        query = query.where(EquipmentModel.is_active == is_active)

    query = query.order_by(EquipmentModel.name)
    result = await db.execute(query)
    models = result.scalars().all()

    return [EquipmentModelResponse.model_validate(m) for m in models]


@router.post("/models", response_model=EquipmentModelResponse, status_code=status.HTTP_201_CREATED)
async def create_model(
    model_data: EquipmentModelCreate,
    db: DB,
    current_user: ManagerUser,
):
    """Create a new equipment model"""
    model = EquipmentModel(**model_data.model_dump())
    db.add(model)
    await db.commit()
    await db.refresh(model)

    return EquipmentModelResponse.model_validate(model)
