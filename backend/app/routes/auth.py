"""
Authentication routes for user registration and login.
Provides endpoints for user registration and JWT token acquisition.
"""

from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordRequestForm, HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel
from db.deps import get_db
from services.security import (
    Token, create_access_token, get_password_hash,
    verify_password, ACCESS_TOKEN_EXPIRE_MINUTES,
    get_current_user
)
from db.models.user import User

router = APIRouter()

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    OAuth2 compatible token login, get an access token for future requests.
    Args:
        form_data: OAuth2 compatible form containing username (email) and password
        db: Database session dependency
    Returns:
        Token: Access token for the user
    Raises:
        HTTPException: If authentication fails
    """
    # Find user by email (username in the form is the email)
    user = db.query(User).filter(User.email == form_data.username).first()
    
    # Verify user exists and password is correct
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register")
async def register(
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Register a new user.
    Args:
        email: User's email address
        password: User's password
        db: Database session dependency
    Returns:
        dict: Success message
    Raises:
        HTTPException: If email is already registered
    """
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(password)
    new_user = User(
        email=email,
        hashed_password=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User created successfully"}

# Example of a protected route
@router.get("/me")
async def read_users_me(current_user = Depends(get_current_user)):
    """
    Test endpoint to get current user information.
    This is an example of a protected route that requires authentication.
    Args:
        current_user: The current authenticated user (from the JWT token)
    Returns:
        dict: Current user information
    """
    return {"email": current_user.email}
