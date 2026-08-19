import time
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.config import settings
from app.schemas import (
    AuthMeResponse, UserProfile
)
from app.services.supabase_service import SupabaseService
from app.utils.logger import logger

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

# Security schemes
security = HTTPBearer()

async def get_current_user_optional(credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))) -> Optional[UserProfile]:
    """
    Dependency to get the current authenticated user, or None if unauthenticated/invalid token.
    """
    if not credentials:
        return None
    token = credentials.credentials
    try:
        supabase_client = SupabaseService.get_client()
        auth_response = supabase_client.auth.get_user(token)
        if not auth_response or not auth_response.user:
            return None
        
        user_id = auth_response.user.id
        email = auth_response.user.email
        phone = auth_response.user.phone
        user_metadata = auth_response.user.user_metadata or {}
        name = user_metadata.get("name") or user_metadata.get("full_name") or "Citizen User"

        # Check/sync profile
        profile = await SupabaseService.get_profile(user_id)
        if not profile:
            profile = await SupabaseService.create_or_update_profile(
                user_id=user_id,
                email=email or "",
                name=name,
                phone_number=phone
            )
        
        if not profile:
            return None

        return UserProfile(
            id=profile["id"],
            email=profile.get("email"),
            phone_number=profile.get("phone_number"),
            name=profile.get("name", "Citizen User"),
            role=profile.get("role", "citizen"),
            created_at=profile.get("created_at") or datetime.now(timezone.utc).isoformat()
        )
    except Exception as e:
        logger.warning(f"Optional auth check failed: {str(e)}")
        return None

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UserProfile:
    """
    Dependency that requires valid authentication and returns the current user profile.
    """
    token = credentials.credentials
    try:
        supabase_client = SupabaseService.get_client()
        auth_response = supabase_client.auth.get_user(token)
        if not auth_response or not auth_response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid session token or expired session",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user_id = auth_response.user.id
        email = auth_response.user.email
        phone = auth_response.user.phone
        user_metadata = auth_response.user.user_metadata or {}
        name = user_metadata.get("name") or user_metadata.get("full_name") or "Citizen User"

        # Check/sync profile
        profile = await SupabaseService.get_profile(user_id)
        if not profile:
            profile = await SupabaseService.create_or_update_profile(
                user_id=user_id,
                email=email or "",
                name=name,
                phone_number=phone
            )
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not retrieve or create user profile"
            )

        return UserProfile(
            id=profile["id"],
            email=profile.get("email"),
            phone_number=profile.get("phone_number"),
            name=profile.get("name", "Citizen User"),
            role=profile.get("role", "citizen"),
            created_at=profile.get("created_at") or datetime.now(timezone.utc).isoformat()
        )
    except Exception as e:
        logger.warning(f"Auth check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired or invalid token, please log in again",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.get("/me", response_model=AuthMeResponse)
async def get_me(user: UserProfile = Depends(get_current_user)):
    """
    Returns the authenticated user's profile.
    """
    return AuthMeResponse(
        authenticated=True,
        user=user
    )

@router.put("/profile", response_model=UserProfile)
async def update_profile(
    name: str,
    user: UserProfile = Depends(get_current_user)
) -> UserProfile:
    """
    Updates the authenticated user's profile information.
    """
    if not name or not name.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Name cannot be empty"
        )
    
    updated_profile = await SupabaseService.create_or_update_profile(
        user_id=user.id,
        email=user.email or "",
        name=name.strip(),
        phone_number=user.phone_number
    )

    if not updated_profile:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile"
        )

    return UserProfile(
        id=updated_profile["id"],
        email=updated_profile.get("email"),
        phone_number=updated_profile.get("phone_number"),
        name=updated_profile.get("name", "Citizen User"),
        role=updated_profile.get("role", "citizen"),
        created_at=updated_profile.get("created_at") or datetime.now(timezone.utc).isoformat()
    )
