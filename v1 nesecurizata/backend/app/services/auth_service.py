import time
from datetime import datetime, timedelta
import random

from sqlalchemy.orm import Session
from app.exceptions import AuthException
from app.models import PasswordResetToken, User, UserRole
from app.security import create_access_token, hash_password, verify_password
from app.services.audit_service import log_event

class AuthService:
    def register(self, db: Session, email: str, password: str, role: str, client_ip: str):
        if db.query(User).filter(User.email == email).first():
            raise AuthException("Email already in use")

        # VULNERABILITY 1: No password length or complexity checks
        hashed_password = hash_password(password)
        parsed_role = self._parse_role(role)

        user = User(
            email=email,
            password_hash=hashed_password,
            role=parsed_role,
            locked=False,
            failed_login_attempts=0,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        log_event(db, user, "REGISTER_SUCCESS", "auth", str(user.id), "User registered", client_ip, True)
        
        token = create_access_token(user.email, user.id, user.role.value)
        return {"token": token, "userId": user.id, "email": user.email, "role": user.role.value, "message": "Registration successful"}

    def login(self, db: Session, email: str, password: str, client_ip: str):
        # VULNERABILITY 2: No Rate Limiting
        user = db.query(User).filter(User.email == email).first()

        # VULNERABILITY 3: User Enumeration (Different messages)
        if not user:
            raise AuthException("User not found")

        if not verify_password(password, user.password_hash):
            raise AuthException("Invalid password")

        log_event(db, user, "LOGIN_SUCCESS", "auth", str(user.id), "Login successful", client_ip, True)
        
        token = create_access_token(user.email, user.id, user.role.value)
        return {"token": token, "userId": user.id, "email": user.email, "role": user.role.value, "message": "Login successful"}

    def forgot_password(self, db: Session, email: str, client_ip: str):
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise AuthException("User not found") # Enumeration leak

        # VULNERABILITY 4: Predictable 6-digit token
        token = str(random.randint(100000, 999999))
        
        # VULNERABILITY 5: Long expiration (24 hours)
        expires_at = datetime.utcnow() + timedelta(hours=24)

        reset_token = PasswordResetToken(token=token, user=user, expires_at=expires_at, used=False)
        db.add(reset_token)
        db.commit()

    def reset_password(self, db: Session, token: str, new_password: str, client_ip: str):
        reset_token = db.query(PasswordResetToken).filter(PasswordResetToken.token == token).first()
        if not reset_token:
            raise AuthException("Invalid reset token")

        # VULNERABILITY 6: Token can be reused (no check for reset_token.used)
        # VULNERABILITY 1: No checks for new_password strength

        user = reset_token.user
        user.password_hash = hash_password(new_password)
        db.commit()

    def _parse_role(self, role_str: str) -> UserRole:
        if not role_str: return UserRole.ANALYST
        try: return UserRole[role_str.strip().upper()]
        except KeyError: return UserRole.ANALYST