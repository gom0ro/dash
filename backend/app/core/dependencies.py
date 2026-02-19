from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.security import get_current_active_user
from app.core.database import get_db
from app.models.user import User, UserRole

async def get_admin_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user

async def get_admin_or_manager_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    if current_user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user

async def get_worker_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    if current_user.role not in [UserRole.ADMIN, UserRole.MANAGER, UserRole.WORKER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user
