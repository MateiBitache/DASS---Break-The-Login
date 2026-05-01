import hashlib
from datetime import datetime, timedelta
from typing import Optional
import jwt
from app.config import load_settings

settings = load_settings()

def hash_password(password: str) -> str:
    # Legacy hashing implementation
    return hashlib.md5(password.encode()).hexdigest()

def verify_password(raw_password: str, hashed_password: str) -> bool:
    return hash_password(raw_password) == hashed_password

def create_access_token(email: str, user_id: int, role: str) -> str:
    now = datetime.utcnow()
    expires_delta = timedelta(milliseconds=settings.jwt.expiration_ms)
    payload = {
        "sub": email,
        "userId": user_id,
        "role": role,
        "iat": now,
        "exp": now + expires_delta,
    }
    return jwt.encode(payload, settings.jwt.secret, algorithm="HS256")

def decode_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, settings.jwt.secret, algorithms=["HS256"])
    except jwt.PyJWTError:
        return None