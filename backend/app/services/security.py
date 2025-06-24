"""
Security utilities for authentication and authorization.
This module handles JWT token creation, password hashing, and user authentication.
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from app.db.deps import get_db
from app.db.models.user import User
from sqlalchemy.orm import Session

# Load environment variables
load_dotenv()

# JWT Configuration - Getting from environment variables
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("JWT_SECRET_KEY environment variable is not set. This is required for security.")

ALGORITHM = os.getenv("JWT_ALGORITHM")
if not ALGORITHM:
    raise ValueError("JWT_ALGORITHM environment variable is not set. This is required for token signing.")

try:
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", ""))
    if ACCESS_TOKEN_EXPIRE_MINUTES <= 0:
        raise ValueError("ACCESS_TOKEN_EXPIRE_MINUTES must be a positive integer")
except (TypeError, ValueError):
    raise ValueError("ACCESS_TOKEN_EXPIRE_MINUTES must be set to a valid positive integer in environment variables")

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme for token handling
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

# Pydantic models for token responses
class Token(BaseModel):
    """Token response model"""
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """Token payload model"""
    email: Optional[str] = None

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.
    Args:
        plain_password: The password in plain text
        hashed_password: The hashed password to compare against
    Returns:
        bool: True if passwords match, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Hash a password for storage.
    Args:
        password: The plain text password to hash
    Returns:
        str: The hashed password
    """
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    Args:
        data: The data to encode in the token
        expires_delta: Optional expiration time delta
    Returns:
        str: The encoded JWT token
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Get the current user from the token.
    This is a dependency that can be used to protect routes.
    Args:
        token: The JWT token from the request
        db: The database session
    Returns:
        User: The current user
    Raises:
        HTTPException: If the token is invalid
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user
