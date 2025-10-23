from fastapi import APIRouter, HTTPException, Depends, status, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Dict, Any
import uuid
from datetime import datetime, timedelta
import jwt
import secrets
import bcrypt

from app.schemas.auth import (
    UserRegisterRequest,
    UserLoginRequest,
    ChangePasswordRequest,
    ForgotPasswordRequest,
    VerifyOTPRequest,
    SetNewPasswordRequest,
    RefreshTokenRequest,
    TokenResponse,
    UserResponse,
    MessageResponse,
)
from app.db.database import get_db
from app.models.user import User
from app.core.config import settings
from app.services.email_service import email_service

# Initialize router
router = APIRouter(prefix="/api/auth", tags=["Auth"])

# Security
security = HTTPBearer()

# Mock JWT settings (replace with your actual settings)
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Mock OTP storage (in production, use Redis or database)
otp_storage: Dict[str, Dict[str, Any]] = {}

# Mock user storage (in production, use database)
users_storage: Dict[str, Dict[str, Any]] = {}

# Mock blacklisted tokens (in production, use Redis)
blacklisted_tokens: set = set()


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """Create JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> dict:
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )


def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(password: str, hashed_password: str) -> bool:
    """Verify password against bcrypt hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))


def generate_otp() -> str:
    """Generate 6-digit OTP"""
    return str(secrets.randbelow(900000) + 100000)


async def send_otp_background(email: str, otp: str):
    """Background task to send OTP email"""
    try:
        email_sent = await email_service.send_otp_email(email, otp, "email_verification")
        if email_sent:
            print(f"✅ OTP email sent successfully to {email}")
        else:
            print(f"❌ Failed to send OTP email to {email}: {otp}")
    except Exception as e:
        print(f"❌ Background email error for {email}: {str(e)}")


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)) -> User:
    """Get current authenticated user"""
    token = credentials.credentials
    
    if token in blacklisted_tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked"
        )
    
    payload = verify_token(token)
    user_id = payload.get("sub")
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    # Get user from database
    user = db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="Create a new user account with email and password"
)
async def register_user(user_data: UserRegisterRequest, db: Session = Depends(get_db)):
    """Register a new user"""
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
        user_id = str(uuid.uuid4())
        hashed_password = hash_password(user_data.password)
        
        new_user = User(
            id=user_id,
            name=user_data.name,
            email=user_data.email,
            password_hash=hashed_password,
            role="USER",
            is_deleted=False
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # Create wallet for the new user with 0 balance (best-effort)
        try:
            from app.models.wallet import Wallet
            wallet = Wallet(
                id=str(uuid.uuid4()),
                user_id=new_user.id,
                balance=0.0,
                total_deposited=0.0,
                total_spent=0.0
            )
            db.add(wallet)
            db.commit()
            print(f"✅ Created wallet for new user: {new_user.email}")
        except Exception as wallet_err:
            db.rollback()
            # Do not fail registration if wallet creation fails
            print(f"⚠️  Could not create wallet for {new_user.email}: {wallet_err}")
        
        # Generate OTP for email verification
        otp_code = generate_otp()
        otp_storage[user_data.email] = {
            "otp": otp_code,
            "expires_at": datetime.now() + timedelta(minutes=10),
            "type": "email_verification"
        }
        
        # Store OTP for verification (no email sent during registration)
        print(f"OTP for {user_data.email}: {otp_code}")
        
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "id": str(new_user.id),
                "name": new_user.name,
                "email": new_user.email,
                "role": new_user.role,
                "is_deleted": new_user.is_deleted,
                "created_at": new_user.created_at.isoformat() if new_user.created_at else None
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="User login",
    description="Authenticate user and return JWT tokens"
)
async def login_user(login_data: UserLoginRequest, db: Session = Depends(get_db)):
    """Login user and return JWT tokens"""
    try:
        # Find user by email
        user = db.query(User).filter(User.email == login_data.email, User.is_deleted == False).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Verify password
        if not verify_password(login_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Create tokens
        access_token = create_access_token({"sub": str(user.id)})
        refresh_token = create_refresh_token({"sub": str(user.id)})
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )


@router.post(
    "/logout",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="User logout",
    description="Invalidate current access token"
)
async def logout_user(current_user: dict = Depends(get_current_user)):
    """Logout user and invalidate token"""
    try:
        # In production, add token to blacklist in Redis
        # For now, we'll just return success
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": "Successfully logged out",
                "success": True
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Logout failed: {str(e)}"
        )


@router.post(
    "/resend-otp",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Resend OTP or Request Password Reset",
    description="Resend OTP for email verification or request password reset OTP"
)
async def resend_otp(request: ForgotPasswordRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Resend OTP for email verification or request password reset"""
    try:
        # Check if user exists in database
        user = db.query(User).filter(User.email == request.email, User.is_deleted == False).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Generate new OTP
        otp_code = generate_otp()
        otp_storage[request.email] = {
            "otp": otp_code,
            "expires_at": datetime.now() + timedelta(minutes=10),
            "type": "email_verification"  # Default to email verification
        }
        
        # Send OTP via email in background (non-blocking)
        background_tasks.add_task(send_otp_background, request.email, otp_code)
        
        # Return response immediately
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": "OTP sent successfully",
                "success": True,
                "otp": otp_code  # Log OTP in response for testing
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to resend OTP: {str(e)}"
        )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Refresh access token",
    description="Get new access token using refresh token"
)
async def refresh_token(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    """Refresh access token using refresh token"""
    try:
        token = request.refresh_token
        payload = verify_token(token)
        
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        # Check if user exists in database
        user = db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        # Create new access token
        access_token = create_access_token({"sub": str(user.id)})
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "access_token": access_token,
                "refresh_token": token,  # Keep the same refresh token
                "token_type": "bearer",
                "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Token refresh failed: {str(e)}"
        )


@router.put(
    "/change-password",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Change password",
    description="Change password for authenticated user"
)
async def change_password(
    password_data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change password for authenticated user"""
    try:
        # Verify current password
        if not verify_password(password_data.current_password, current_user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Update password in database
        new_password_hash = hash_password(password_data.new_password)
        current_user.password_hash = new_password_hash
        db.commit()
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": "Password changed successfully",
                "success": True
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Password change failed: {str(e)}"
        )



@router.post(
    "/verify-reset-otp",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Verify reset OTP",
    description="Verify OTP code for password reset"
)
async def verify_reset_otp(request: VerifyOTPRequest):
    """Verify OTP for password reset"""
    try:
        # Check if OTP exists and is valid
        if request.email not in otp_storage:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No OTP found for this email"
            )
        
        stored_otp = otp_storage[request.email]
        
        # Check if OTP has expired
        if datetime.now() > stored_otp["expires_at"]:
            del otp_storage[request.email]
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="OTP has expired"
            )
        
        # Check OTP code
        if stored_otp["otp"] != request.otp_code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid OTP code"
            )
        
        # Mark OTP as verified
        otp_storage[request.email]["verified"] = True
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": "OTP verified successfully",
                "success": True
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OTP verification failed: {str(e)}"
        )


@router.post(
    "/set-new-password",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Set new password",
    description="Set new password after OTP verification"
)
async def set_new_password(request: SetNewPasswordRequest, db: Session = Depends(get_db)):
    """Set new password after OTP verification"""
    try:
        # Check if OTP exists and is verified
        if request.email not in otp_storage:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No OTP found for this email"
            )
        
        stored_otp = otp_storage[request.email]
        
        # Check if OTP is verified
        if not stored_otp.get("verified", False):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="OTP not verified. Please verify OTP first."
            )
        
        # Check OTP code (double verification)
        if stored_otp["otp"] != request.otp_code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid OTP code"
            )
        
        # Find user in database
        user = db.query(User).filter(User.email == request.email, User.is_deleted == False).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update password in database
        new_password_hash = hash_password(request.new_password)
        user.password_hash = new_password_hash
        db.commit()
        
        # Remove OTP from storage
        del otp_storage[request.email]
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": "Password reset successfully",
                "success": True
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Password reset failed: {str(e)}"
        )
