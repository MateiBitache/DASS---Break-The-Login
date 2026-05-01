from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from app.models import TicketSeverity, TicketStatus, UserRole


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1)
    role: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    token: str
    type: str = "Bearer"
    userId: int
    email: str
    role: str
    message: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    newPassword: str


class CreateTicketRequest(BaseModel):
    title: str
    description: Optional[str] = None
    severity: Optional[TicketSeverity] = None


class TicketDTO(BaseModel):
    id: int
    title: str
    description: Optional[str]
    severity: TicketSeverity
    status: TicketStatus
    ownerId: int
    ownerEmail: str
    createdAt: datetime
    updatedAt: Optional[datetime]

    class Config:
        from_attributes = True
