"""
Authentication service
"""
from typing import Optional, Dict, Any
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from jose import JWTError, jwt
import secrets
import logging

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = "your-secret-key-change-in-production"  # Should be in .env
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days


class AuthService:
    """Service for authentication operations"""
    
    def __init__(self, db):
        self.db = db
        self.users_collection = db.users
        self.password_resets_collection = db.password_resets
    
    def hash_password(self, password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError:
            return None
    
    async def register_user(self, email: str, password: str, full_name: str, phone: str) -> Dict[str, Any]:
        """Register a new user"""
        # Check if user exists
        existing_user = await self.users_collection.find_one({"email": email.lower()})
        if existing_user:
            raise ValueError("User with this email already exists")
        
        # Create user document
        user_doc = {
            "id": str(secrets.token_urlsafe(16)),
            "email": email.lower(),
            "password_hash": self.hash_password(password),
            "full_name": full_name,
            "phone": phone,
            "is_verified": False,
            "auth_provider": "email",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Insert user
        await self.users_collection.insert_one(user_doc)
        
        # Return user (without password)
        user_doc.pop("password_hash", None)
        return user_doc
    
    async def login_user(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Login user and return token"""
        user = await self.users_collection.find_one({"email": email.lower()})
        if not user:
            return None
        
        if not self.verify_password(password, user.get("password_hash", "")):
            return None
        
        # Create token
        token_data = {
            "sub": user["id"],
            "email": user["email"]
        }
        access_token = self.create_access_token(token_data)
        
        # Return user and token
        user_doc = dict(user)
        user_doc.pop("password_hash", None)
        return {
            "access_token": access_token,
            "user": user_doc
        }
    
    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        user = await self.users_collection.find_one({"id": user_id})
        if user:
            user_doc = dict(user)
            user_doc.pop("password_hash", None)
            return user_doc
        return None
    
    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        user = await self.users_collection.find_one({"email": email.lower()})
        if user:
            user_doc = dict(user)
            user_doc.pop("password_hash", None)
            return user_doc
        return None
    
    async def google_auth(self, google_id_token: str, full_name: Optional[str] = None, phone: Optional[str] = None) -> Dict[str, Any]:
        """Handle Google OAuth authentication"""
        # In production, verify the Google ID token here
        # For now, we'll create/update user based on token
        # This is a simplified version - you should verify the token with Google
        
        # Extract email from token (in production, verify with Google first)
        # For now, we'll use a placeholder
        # TODO: Verify Google ID token with Google's API
        
        # This is a placeholder - implement proper Google token verification
        raise NotImplementedError("Google OAuth verification not yet implemented. Use email/password for now.")
    
    async def create_password_reset_token(self, email: str) -> str:
        """Create password reset token"""
        user = await self.users_collection.find_one({"email": email.lower()})
        if not user:
            return None  # Don't reveal if user exists
        
        reset_token = secrets.token_urlsafe(32)
        reset_doc = {
            "email": email.lower(),
            "token": reset_token,
            "expires_at": (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat(),
            "used": False,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        await self.password_resets_collection.insert_one(reset_doc)
        return reset_token
    
    async def reset_password(self, token: str, new_password: str) -> bool:
        """Reset password using token"""
        reset_doc = await self.password_resets_collection.find_one({"token": token, "used": False})
        if not reset_doc:
            return False
        
        # Check if expired
        expires_at = datetime.fromisoformat(reset_doc["expires_at"])
        if datetime.now(timezone.utc) > expires_at:
            return False
        
        # Update password
        await self.users_collection.update_one(
            {"email": reset_doc["email"]},
            {"$set": {
                "password_hash": self.hash_password(new_password),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        
        # Mark token as used
        await self.password_resets_collection.update_one(
            {"token": token},
            {"$set": {"used": True}}
        )
        
        return True



