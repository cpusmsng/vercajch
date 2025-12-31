from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_db, get_current_user, get_user_role, get_role_permissions
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    verify_refresh_token,
)
from app.models.user import User
from app.schemas.auth import Token, Login, LoginResponse, PasswordChange
from app.schemas.user import UserResponse, UserWithPermissions

router = APIRouter()


@router.post("/login", response_model=LoginResponse)
async def login(
    login_data: Login,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Login with email and password"""
    result = await db.execute(
        select(User)
        .options(selectinload(User.role), selectinload(User.department))
        .where(User.email == login_data.email)
    )
    user = result.scalar_one_or_none()

    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    # Update last login
    user.last_login_at = datetime.utcnow()
    user.last_login_platform = "mobile"
    await db.commit()
    await db.refresh(user)

    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token(str(user.id))

    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user=UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            phone=user.phone,
            employee_number=user.employee_number,
            role_id=user.role_id,
            role=user.role,
            department_id=user.department_id,
            department=user.department,
            manager_id=user.manager_id,
            is_active=user.is_active,
            can_access_web=user.can_access_web,
            can_access_mobile=user.can_access_mobile,
            avatar_url=user.avatar_url,
            last_login_at=user.last_login_at,
            last_login_platform=user.last_login_platform,
            created_at=user.created_at
        )
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token: Annotated[str, Query(description="Refresh token")],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Refresh access token using refresh token"""
    user_id = verify_refresh_token(refresh_token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )

    result = await db.execute(
        select(User).where(User.id == UUID(user_id))
    )
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )

    access_token = create_access_token(str(user.id))
    new_refresh_token = create_refresh_token(str(user.id))

    return Token(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer"
    )


@router.post("/logout")
async def logout():
    """Logout current user"""
    # In a stateless JWT setup, logout is handled client-side
    # For added security, you could implement token blacklisting with Redis
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserWithPermissions)
async def get_current_user_info(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Get current user info with permissions"""
    # Reload user with relationships
    result = await db.execute(
        select(User)
        .options(selectinload(User.role), selectinload(User.department))
        .where(User.id == current_user.id)
    )
    user = result.scalar_one()

    # Get permissions for user's role
    user_role = get_user_role(user)
    permissions = [p.value for p in get_role_permissions(user_role)]

    return UserWithPermissions(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        phone=user.phone,
        employee_number=user.employee_number,
        role_id=user.role_id,
        role=user.role,
        department_id=user.department_id,
        department=user.department,
        manager_id=user.manager_id,
        is_active=user.is_active,
        can_access_web=user.can_access_web,
        can_access_mobile=user.can_access_mobile,
        avatar_url=user.avatar_url,
        last_login_at=user.last_login_at,
        last_login_platform=user.last_login_platform,
        created_at=user.created_at,
        permissions=permissions
    )


@router.put("/password")
async def change_password(
    password_data: PasswordChange,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Change current user's password"""
    if not verify_password(password_data.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )

    current_user.password_hash = get_password_hash(password_data.new_password)
    await db.commit()

    return {"message": "Password changed successfully"}
