from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.services.auth_service import AuthService
from app.schemas.auth import Token, UserCreate, UserLogin, UserResponse

router = APIRouter()


@router.post("/register", response_model=UserResponse)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_async_session),
):
    """Register a new user account."""
    auth_service = AuthService(db)
    
    # Check if user already exists
    existing_user = await auth_service.get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    user = await auth_service.create_user(user_data)
    return user


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_async_session),
):
    """Login user and return access token."""
    auth_service = AuthService(db)
    
    user = await auth_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = await auth_service.create_access_token(user.id)
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token: str,
    db: AsyncSession = Depends(get_async_session),
):
    """Refresh access token using refresh token."""
    auth_service = AuthService(db)
    
    try:
        new_access_token = await auth_service.refresh_access_token(refresh_token)
        return {
            "access_token": new_access_token,
            "token_type": "bearer"
        }
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/logout")
async def logout(
    token: str,
    db: AsyncSession = Depends(get_async_session),
):
    """Logout user by invalidating token."""
    auth_service = AuthService(db)
    await auth_service.revoke_token(token)
    return {"message": "Successfully logged out"}


@router.post("/forgot-password")
async def forgot_password(
    email: str,
    db: AsyncSession = Depends(get_async_session),
):
    """Send password reset email."""
    auth_service = AuthService(db)
    await auth_service.send_password_reset_email(email)
    return {"message": "Password reset email sent if account exists"}


@router.post("/reset-password")
async def reset_password(
    token: str,
    new_password: str,
    db: AsyncSession = Depends(get_async_session),
):
    """Reset password using reset token."""
    auth_service = AuthService(db)
    
    try:
        await auth_service.reset_password(token, new_password)
        return {"message": "Password reset successfully"}
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
