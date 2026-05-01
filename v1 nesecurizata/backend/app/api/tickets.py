from fastapi import APIRouter, Depends, Header, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.exceptions import AuthException
from app.schemas import CreateTicketRequest, TicketDTO
from app.security import decode_token
from app.services import ticket_service

router = APIRouter(prefix="/api/tickets", tags=["tickets"])


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host


def _get_user_id(authorization: str = Header(None)) -> int:
    if not authorization or not authorization.startswith("Bearer "):
        raise AuthException("Invalid credentials")
    token = authorization.split(" ", 1)[1]
    payload = decode_token(token)
    if not payload or "userId" not in payload:
        raise AuthException("Invalid credentials")
    return int(payload["userId"])


@router.post("", response_model=TicketDTO)
def create_ticket(
    request_data: CreateTicketRequest,
    request: Request,
    db: Session = Depends(get_db),
    user_id: int = Depends(_get_user_id),
):
    ticket = ticket_service.create_ticket(db, user_id, request_data, _client_ip(request))
    return TicketDTO(
        id=ticket.id,
        title=ticket.title,
        description=ticket.description,
        severity=ticket.severity,
        status=ticket.status,
        ownerId=ticket.owner_id,
        ownerEmail=ticket.owner.email,
        createdAt=ticket.created_at,
        updatedAt=ticket.updated_at,
    )


@router.get("", response_model=list[TicketDTO])
def get_tickets(db: Session = Depends(get_db), user_id: int = Depends(_get_user_id)):
    tickets = ticket_service.get_my_tickets(db, user_id)
    return [
        TicketDTO(
            id=ticket.id,
            title=ticket.title,
            description=ticket.description,
            severity=ticket.severity,
            status=ticket.status,
            ownerId=ticket.owner_id,
            ownerEmail=ticket.owner.email,
            createdAt=ticket.created_at,
            updatedAt=ticket.updated_at,
        )
        for ticket in tickets
    ]


@router.get("/search", response_model=list[TicketDTO])
def search_tickets(
    q: str,
    db: Session = Depends(get_db),
    user_id: int = Depends(_get_user_id),
):
    tickets = ticket_service.search_tickets(db, user_id, q)
    return [
        TicketDTO(
            id=ticket.id,
            title=ticket.title,
            description=ticket.description,
            severity=ticket.severity,
            status=ticket.status,
            ownerId=ticket.owner_id,
            ownerEmail=ticket.owner.email,
            createdAt=ticket.created_at,
            updatedAt=ticket.updated_at,
        )
        for ticket in tickets
    ]


@router.get("/{ticket_id}", response_model=TicketDTO)
def get_ticket(
    ticket_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user_id: int = Depends(_get_user_id),
):
    ticket = ticket_service.get_ticket(db, user_id, ticket_id, _client_ip(request))
    return TicketDTO(
        id=ticket.id,
        title=ticket.title,
        description=ticket.description,
        severity=ticket.severity,
        status=ticket.status,
        ownerId=ticket.owner_id,
        ownerEmail=ticket.owner.email,
        createdAt=ticket.created_at,
        updatedAt=ticket.updated_at,
    )


@router.put("/{ticket_id}", response_model=TicketDTO)
def update_ticket(
    ticket_id: int,
    request_data: CreateTicketRequest,
    request: Request,
    db: Session = Depends(get_db),
    user_id: int = Depends(_get_user_id),
):
    ticket = ticket_service.update_ticket(
        db, user_id, ticket_id, request_data, _client_ip(request)
    )
    return TicketDTO(
        id=ticket.id,
        title=ticket.title,
        description=ticket.description,
        severity=ticket.severity,
        status=ticket.status,
        ownerId=ticket.owner_id,
        ownerEmail=ticket.owner.email,
        createdAt=ticket.created_at,
        updatedAt=ticket.updated_at,
    )


@router.delete("/{ticket_id}", status_code=204)
def delete_ticket(
    ticket_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user_id: int = Depends(_get_user_id),
):
    ticket_service.delete_ticket(db, user_id, ticket_id, _client_ip(request))
