from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, status, Query
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.api.deps import DB, CurrentUser, ManagerUser, AdminUser
from app.models.equipment import Category
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse, CategoryTree

router = APIRouter()


@router.get("", response_model=List[CategoryResponse])
async def list_categories(
    db: DB,
    current_user: CurrentUser,
    parent_id: Optional[UUID] = None,
):
    """List categories"""
    query = select(Category)

    if parent_id:
        query = query.where(Category.parent_category_id == parent_id)
    else:
        query = query.where(Category.parent_category_id.is_(None))

    query = query.order_by(Category.name)
    result = await db.execute(query)
    categories = result.scalars().all()

    return [CategoryResponse.model_validate(c) for c in categories]


@router.get("/tree", response_model=List[CategoryTree])
async def get_category_tree(
    db: DB,
    current_user: CurrentUser,
):
    """Get category tree structure"""
    result = await db.execute(
        select(Category)
        .options(selectinload(Category.children))
        .where(Category.parent_category_id.is_(None))
        .order_by(Category.name)
    )
    root_categories = result.scalars().all()

    async def build_tree(category: Category) -> CategoryTree:
        children_result = await db.execute(
            select(Category)
            .where(Category.parent_category_id == category.id)
            .order_by(Category.name)
        )
        children = children_result.scalars().all()

        return CategoryTree(
            id=category.id,
            name=category.name,
            code=category.code,
            parent_category_id=category.parent_category_id,
            default_maintenance_interval_days=category.default_maintenance_interval_days,
            requires_certification=category.requires_certification,
            transfer_requires_approval=category.transfer_requires_approval,
            max_transfer_days=category.max_transfer_days,
            icon=category.icon,
            color=category.color,
            created_at=category.created_at,
            children=[await build_tree(c) for c in children]
        )

    return [await build_tree(c) for c in root_categories]


@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_data: CategoryCreate,
    db: DB,
    current_user: ManagerUser,
):
    """Create a new category"""
    category = Category(**category_data.model_dump())
    db.add(category)
    await db.commit()
    await db.refresh(category)

    return CategoryResponse.model_validate(category)


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: UUID,
    db: DB,
    current_user: CurrentUser,
):
    """Get category by ID"""
    result = await db.execute(
        select(Category).where(Category.id == category_id)
    )
    category = result.scalar_one_or_none()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    return CategoryResponse.model_validate(category)


@router.put("/{category_id}", response_model=CategoryResponse)
@router.patch("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: UUID,
    category_data: CategoryUpdate,
    db: DB,
    current_user: ManagerUser,
):
    """Update a category"""
    result = await db.execute(
        select(Category).where(Category.id == category_id)
    )
    category = result.scalar_one_or_none()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    update_data = category_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(category, field, value)

    await db.commit()
    await db.refresh(category)

    return CategoryResponse.model_validate(category)


@router.delete("/{category_id}")
async def delete_category(
    category_id: UUID,
    db: DB,
    current_user: AdminUser,
):
    """Delete a category"""
    result = await db.execute(
        select(Category).where(Category.id == category_id)
    )
    category = result.scalar_one_or_none()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    # Check if category has equipment
    from app.models.equipment import Equipment
    equipment_result = await db.execute(
        select(Equipment).where(Equipment.category_id == category_id).limit(1)
    )
    if equipment_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete category with assigned equipment"
        )

    await db.delete(category)
    await db.commit()

    return {"message": "Category deleted successfully"}
