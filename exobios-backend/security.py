# backend/security.py
import os
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from fastapi.security import OAuth2PasswordBearer

# Security Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "exobios_super_secret_key_change_in_production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480 # 8-hour shift

# OAuth2 scheme for JWT token validation
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Safely verifies a plain password against the hashed version using direct bcrypt."""
    password_bytes = plain_password.encode('utf-8')
    hash_bytes = hashed_password.encode('utf-8')
    try:
        return bcrypt.checkpw(password_bytes, hash_bytes)
    except ValueError:
        return False

def get_password_hash(password: str) -> str:
    """Hashes a password using modern bcrypt (with a safe 72-byte truncation limit)."""
    password_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password_bytes, salt)
    return hashed_password.decode('utf-8')

def create_access_token(data: dict):
    """Generates a secure JWT token for user sessions."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    # Generate the JWT
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_access_token(token: str):
    """Verify JWT token and return payload if valid, None otherwise"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None