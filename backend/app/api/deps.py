from typing import Optional, Annotated
from uuid import UUID
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import verify_access_token
from app.core.permissions import Permission, Role, has_permission, get_role_permissions
from app.models.user import User, Role as RoleModel

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


async def get_current_user(
    db: Annotated[AsyncSession, Depends(get_db)],
    token: Annotated[Optional[str], Depends(oauth2_scheme)]
) -> User:
    """Get current authenticated user"""
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = verify_access_token(token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    result = await db.execute(
        select(User).where(User.id == UUID(user_id))
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is inactive"
        )

    return user


async def get_current_user_optional(
    db: Annotated[AsyncSession, Depends(get_db)],
    token: Annotated[Optional[str], Depends(oauth2_scheme)]
) -> Optional[User]:
    """Get current user if authenticated, None otherwise"""
    if not token:
        return None

    user_id = verify_access_token(token)
    if not user_id:
        return None

    result = await db.execute(
        select(User).where(User.id == UUID(user_id))
    )
    user = result.scalar_one_or_none()

    if user and user.is_active:
        return user
    return None


def get_user_role(user: User) -> Role:
    """Get the Role enum from user's role"""
    if not user.role:
        return Role.WORKER
    return Role(user.role.code)


def check_permission(permission: Permission):
    """Dependency factory to check if user has a specific permission"""
    async def permission_checker(
        current_user: Annotated[User, Depends(get_current_user)]
    ) -> User:
        user_role = get_user_role(current_user)
        if not has_permission(user_role, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {permission.value}"
            )
        return current_user
    return permission_checker


def check_any_permission(*permissions: Permission):
    """Dependency factory to check if user has any of the specified permissions"""
    async def permission_checker(
        current_user: Annotated[User, Depends(get_current_user)]
    ) -> User:
        user_role = get_user_role(current_user)
        user_permissions = get_role_permissions(user_role)

        if not any(p in user_permissions for p in permissions):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permission denied"
            )
        return current_user
    return permission_checker


def check_role(*roles: Role):
    """Dependency factory to check if user has one of the specified roles"""
    async def role_checker(
        current_user: Annotated[User, Depends(get_current_user)]
    ) -> User:
        user_role = get_user_role(current_user)
        if user_role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role required: {', '.join(r.value for r in roles)}"
            )
        return current_user
    return role_checker


# Common dependencies
CurrentUser = Annotated[User, Depends(get_current_user)]
OptionalUser = Annotated[Optional[User], Depends(get_current_user_optional)]
DB = Annotated[AsyncSession, Depends(get_db)]

# Role-based dependencies
AdminUser = Annotated[User, Depends(check_role(Role.ADMIN, Role.SUPERADMIN))]
ManagerUser = Annotated[User, Depends(check_role(Role.MANAGER, Role.ADMIN, Role.SUPERADMIN))]
LeaderUser = Annotated[User, Depends(check_role(Role.LEADER, Role.MANAGER, Role.ADMIN, Role.SUPERADMIN))]
