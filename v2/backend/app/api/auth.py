from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.exceptions import AuthException
from app.schemas import AuthResponse, ForgotPasswordRequest, LoginRequest, RegisterRequest, ResetPasswordRequest
from app.services.auth_service import AuthService

router = APIRouter(prefix="/api/auth", tags=["auth"])
service = AuthService()


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host


@router.post("/register", response_model=AuthResponse)
def register(request_data: RegisterRequest, request: Request, db: Session = Depends(get_db)):
    response = service.register(
        db,
        request_data.email,
        request_data.password,
        request_data.role,
        _client_ip(request),
    )
    return response


@router.post("/login", response_model=AuthResponse)
def login(request_data: LoginRequest, request: Request, db: Session = Depends(get_db)):
    response = service.login(
        db,
        request_data.email,
        request_data.password,
        _client_ip(request),
    )
    return response


@router.post("/forgot-password")
def forgot_password(
    request_data: ForgotPasswordRequest, request: Request, db: Session = Depends(get_db)
):
    service.forgot_password(db, request_data.email, _client_ip(request))
    return {"message": "If the email exists, a password reset link has been sent"}


@router.post("/reset-password")
def reset_password(
    request_data: ResetPasswordRequest, request: Request, db: Session = Depends(get_db)
):
    service.reset_password(
        db, request_data.token, request_data.newPassword, _client_ip(request)
    )
    return {"message": "Password has been successfully reset"}


@router.post("/logout")
def logout():
    return {"message": "Logout successful"}
