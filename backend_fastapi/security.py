import os
import jwt
import bcrypt
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database import get_db
from models import User

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "super-secret-jwt-key-2026")
ALGORITHM = "HS256"
security_scheme = HTTPBearer()

def hash_password(plain_password: str) -> str:
    return bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

def create_access_token(user: User) -> str:
    payload = {
        "sub": str(user.id),
        "user_id": user.id,
        "email": user.email,
        "role": user.role,
        "exp": datetime.now(timezone.utc) + timedelta(hours=12),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: Session = Depends(get_db),
) -> User:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = int(payload.get("user_id"))
    except (jwt.PyJWTError, ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired JWT token",
        )
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    if user.is_blocked:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account is blocked")
    return user

def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required to access this endpoint",
        )
    return current_user
