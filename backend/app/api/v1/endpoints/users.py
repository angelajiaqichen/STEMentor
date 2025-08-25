from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.services.user_service import UserService
from app.services.auth_service import get_current_user
from app.schemas.user import UserProfile, UserUpdate, UserResponse
from app.models.user import User

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
):
    """Get current user's profile information."""
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_current_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    """Update current user's profile information."""
    user_service = UserService(db)
    updated_user = await user_service.update_user(current_user.id, user_update)
    return updated_user


@router.get("/me/profile", response_model=UserProfile)
async def get_detailed_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    """Get detailed user profile including learning preferences and statistics."""
    user_service = UserService(db)
    profile = await user_service.get_detailed_profile(current_user.id)
    return profile


@router.post("/me/preferences")
async def update_learning_preferences(
    preferences: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    """Update user's learning preferences and settings."""
    user_service = UserService(db)
    await user_service.update_learning_preferences(current_user.id, preferences)
    return {"message": "Learning preferences updated successfully"}


@router.delete("/me")
async def delete_current_user_account(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    """Delete current user's account and all associated data."""
    user_service = UserService(db)
    await user_service.delete_user_account(current_user.id)
    return {"message": "Account deleted successfully"}


@router.post("/me/change-password")
async def change_password(
    current_password: str,
    new_password: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    """Change user's password."""
    user_service = UserService(db)
    
    # Verify current password
    if not await user_service.verify_password(current_user.id, current_password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    
    await user_service.update_password(current_user.id, new_password)
    return {"message": "Password changed successfully"}
