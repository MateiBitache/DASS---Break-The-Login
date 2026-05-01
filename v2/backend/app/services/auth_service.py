import time
from datetime import datetime, timedelta
import secrets

from sqlalchemy.orm import Session
from app.exceptions import AuthException
from app.models import PasswordResetToken, User, UserRole
from app.security import create_access_token, hash_password, verify_password
from app.services.audit_service import log_event
from app.services.rate_limit_service import RateLimitService

class AuthService:
    def __init__(self):
        self.rate_limit_service = RateLimitService()

    def register(self, db: Session, email: str, password: str, role: str, client_ip: str):
        if db.query(User).filter(User.email == email).first():
            # Enum prevention: Generic message could be used, but standard validation is fine here
            raise AuthException("Registration failed or email in use")

        # Strict password policy
        if len(password) < 12:
            raise AuthException("Password must be at least 12 characters")

        if not self._is_password_complex(password):
            raise AuthException("Password must contain uppercase, lowercase, digit, and special character")

        hashed_password = hash_password(password)
        user = User(email=email, password_hash=hashed_password, role=self._parse_role(role), locked=False, failed_login_attempts=0)
        db.add(user)
        db.commit()
        db.refresh(user)

        log_event(db, user, "REGISTER_SUCCESS", "auth", str(user.id), "User registered safely", client_ip, True)
        
        token = create_access_token(user.email, user.id, user.role.value)
        return {"token": token, "userId": user.id, "email": user.email, "role": user.role.value, "message": "Registration successful"}

    def login(self, db: Session, email: str, password: str, client_ip: str):
        # Enforce Rate Limiting against Brute Force
        self.rate_limit_service.check_rate_limit(email, client_ip)
        start_time = time.time()

        try:
            user = db.query(User).filter(User.email == email).first()

            if not user:
                # Prevent User Enumeration (Uniform response time & generic message)
                self._simulate_password_check()
                self._sleep_to_uniform_time(start_time, 0.2)
                raise AuthException("Invalid credentials")

            if user.locked and user.lockout_until and datetime.utcnow() < user.lockout_until:
                raise AuthException("Account is temporarily locked. Try again later.")

            if not verify_password(password, user.password_hash):
                user.failed_login_attempts += 1
                if user.failed_login_attempts >= 5:
                    user.locked = True
                    user.lockout_until = datetime.utcnow() + timedelta(minutes=15)
                db.commit()
                
                # Prevent User Enumeration
                self._sleep_to_uniform_time(start_time, 0.2)
                raise AuthException("Invalid credentials")

            user.failed_login_attempts = 0
            user.locked = False
            user.lockout_until = None
            db.commit()

            token = create_access_token(user.email, user.id, user.role.value)
            return {"token": token, "userId": user.id, "email": user.email, "role": user.role.value, "message": "Login successful"}
        except AuthException:
            raise

    def forgot_password(self, db: Session, email: str, client_ip: str):
        self.rate_limit_service.check_rate_limit(email, client_ip)
        user = db.query(User).filter(User.email == email).first()

        # Don't reveal if email exists (Return generic regardless)
        if not user: return 

        db.query(PasswordResetToken).filter(PasswordResetToken.user_id == user.id).delete()

        # Cryptographically strong token & short expiration (15 mins)
        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(minutes=15)

        reset_token = PasswordResetToken(token=token, user=user, expires_at=expires_at, used=False)
        db.add(reset_token)
        db.commit()

    def reset_password(self, db: Session, token: str, new_password: str, client_ip: str):
        reset_token = db.query(PasswordResetToken).filter(PasswordResetToken.token == token).first()
        
        if not reset_token or reset_token.is_expired(datetime.utcnow()):
            raise AuthException("Invalid or expired reset token")

        # Token One-Time Use prevention
        if reset_token.used:
            raise AuthException("Reset token has already been used")

        # Enforce policy on new password
        if len(new_password) < 12 or not self._is_password_complex(new_password):
            raise AuthException("Password does not meet complexity requirements")

        user = reset_token.user
        user.password_hash = hash_password(new_password)
        user.failed_login_attempts = 0
        user.locked = False
        
        reset_token.used = True
        reset_token.used_at = datetime.utcnow()
        db.commit()

    def _parse_role(self, role_str: str) -> UserRole:
        if not role_str: return UserRole.ANALYST
        try: return UserRole[role_str.strip().upper()]
        except KeyError: return UserRole.ANALYST

    def _is_password_complex(self, password: str) -> bool:
        return (len(password) >= 12 and any(ch.isupper() for ch in password) and 
                any(ch.islower() for ch in password) and any(ch.isdigit() for ch in password) and 
                any(ch in "!@#$%^&*()_+-=[]{}|;:,.<>?" for ch in password))

    def _simulate_password_check(self): time.sleep(0.05)
    def _sleep_to_uniform_time(self, start_time: float, target_seconds: float):
        elapsed = time.time() - start_time
        if elapsed < target_seconds: time.sleep(target_seconds - elapsed)