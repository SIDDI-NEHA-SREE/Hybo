import time
import uuid
import random
import jwt
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.config import settings
from app.schemas import (
    SendOTPRequest, SendOTPResponse,
    VerifyOTPRequest, VerifyOTPResponse,
    AuthMeResponse, UserProfile
)
from app.services.twilio_service import TwilioService
from app.utils.logger import logger

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

# In-memory stores (since no DB config is specified in requirements.txt)
# otp_store maps normalized_phone_number -> { "otp": str, "expires_at": float, "name": Optional[str] }
otp_store: Dict[str, Dict[str, Any]] = {}

# users_db maps user_id -> UserProfile
users_db: Dict[str, UserProfile] = {}

# Security schemes
security = HTTPBearer()

def get_current_user_optional(credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))) -> Optional[UserProfile]:
    """
    Dependency to get the current authenticated user, or None if unauthenticated/invalid token.
    """
    if not credentials:
        return None
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            return None
        return users_db.get(user_id)
    except Exception:
        return None

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UserProfile:
    """
    Dependency that requires valid authentication and returns the current user profile.
    """
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token is missing subject claim",
                headers={"WWW-Authenticate": "Bearer"},
            )
        user = users_db.get(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found in system",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired, please log in again",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.PyJWTError as e:
        logger.warning(f"JWT verification failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid session token",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.post("/send-otp", response_model=SendOTPResponse)
async def send_otp(request: SendOTPRequest):
    """
    Initiates authentication by generating and sending an OTP to the phone number.
    If Twilio is not configured, it runs in Dev Fallback Mode.
    """
    phone_number = request.phone_number
    name = request.name
    normalized_phone = TwilioService.normalize_phone_number(phone_number)
    
    # Generate 6-digit OTP
    otp = "".join([str(random.randint(0, 9)) for _ in range(6)])
    
    # Send via Twilio (or Dev Fallback)
    success, message, dev_mode = TwilioService.send_sms_otp(normalized_phone, otp)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=message
        )
    
    # Store OTP in-memory
    otp_store[normalized_phone] = {
        "otp": otp,
        "expires_at": time.time() + (settings.OTP_EXPIRE_MINUTES * 60),
        "name": name
    }
    
    response = SendOTPResponse(
        success=True,
        message=message,
        phone_number=normalized_phone,
        dev_mode=dev_mode
    )
    
    if dev_mode:
        response.dev_otp = otp
        
    return response

@router.post("/verify-otp", response_model=VerifyOTPResponse)
async def verify_otp(request: VerifyOTPRequest):
    """
    Verifies the OTP code. On success, logs the user in (or registers them)
    and returns a JWT bearer access token.
    """
    phone_number = request.phone_number
    otp_code = request.otp
    name = request.name
    
    normalized_phone = TwilioService.normalize_phone_number(phone_number)
    
    # If Twilio Verify is configured, we use its API
    is_verified = False
    verification_message = "OTP verification successful"
    
    if settings.is_twilio_configured and settings.TWILIO_VERIFY_SERVICE_SID:
        is_verified, verification_message = TwilioService.verify_with_twilio_service(normalized_phone, otp_code)
    else:
        # Check in local memory store
        stored = otp_store.get(normalized_phone)
        if not stored:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No active OTP request found for this phone number"
            )
        
        # Check expiry
        if time.time() > stored["expires_at"]:
            otp_store.pop(normalized_phone, None)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="OTP code has expired. Please request a new one."
            )
            
        # Verify code
        if stored["otp"] == otp_code:
            is_verified = True
            # Clean up the used OTP
            otp_store.pop(normalized_phone, None)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect OTP code. Please try again."
            )
            
    if not is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=verification_message
        )
        
    # User Lookup / Registration
    user = None
    for u in users_db.values():
        if u.phone_number == normalized_phone:
            user = u
            break
            
    if not user:
        # Create a new user profile
        user_id = str(uuid.uuid4())
        user_name = name or (stored.get("name") if 'stored' in locals() else None) or "Citizen User"
        user = UserProfile(
            id=user_id,
            phone_number=normalized_phone,
            name=user_name,
            role="citizen",
            created_at=datetime.now(timezone.utc).isoformat()
        )
        users_db[user_id] = user
        logger.info(f"Registered new user: ID {user_id}, Name '{user_name}', Phone {normalized_phone}")
    else:
        # Update name if new name is provided during login
        if name:
            user.name = name
            users_db[user.id] = user
            logger.info(f"Updated name for user {user.id} to '{name}'")
            
    # Generate JWT Token
    token_expiry = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token_payload = {
        "sub": user.id,
        "exp": token_expiry
    }
    
    access_token = jwt.encode(
        token_payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    
    return VerifyOTPResponse(
        success=True,
        message="Login successful",
        access_token=access_token,
        token_type="bearer",
        user=user
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
):
    """
    Updates the authenticated user's profile information.
    """
    if not name or not name.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Name cannot be empty"
        )
        
    user.name = name.strip()
    users_db[user.id] = user
    logger.info(f"User {user.id} updated their name to '{user.name}'")
    return user
