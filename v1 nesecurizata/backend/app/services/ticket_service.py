from sqlalchemy.orm import Session
from app.exceptions import AuthException
from app.models import Ticket, TicketSeverity, TicketStatus, User
from app.services.audit_service import log_event

def create_ticket(db: Session, user_id: int, request, client_ip: str):
    user = db.query(User).filter(User.id == user_id).first()
    severity = request.severity or TicketSeverity.MEDIUM

    ticket = Ticket(title=request.title, description=request.description, severity=severity, status=TicketStatus.OPEN, owner=user)
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket

def get_my_tickets(db: Session, user_id: int):
    return db.query(Ticket).filter(Ticket.owner_id == user_id).all()

def get_ticket(db: Session, user_id: int, ticket_id: int, client_ip: str):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket: raise AuthException("Ticket not found")
    
    # VULNERABILITY: Missing IDOR check (ticket.owner_id != user_id)
    return ticket

def update_ticket(db: Session, user_id: int, ticket_id: int, request, client_ip: str):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket: raise AuthException("Ticket not found")

    # VULNERABILITY: Missing IDOR check
    if request.title is not None: ticket.title = request.title
    if request.description is not None: ticket.description = request.description
    if request.severity is not None: ticket.severity = request.severity

    db.commit()
    db.refresh(ticket)
    return ticket

def delete_ticket(db: Session, user_id: int, ticket_id: int, client_ip: str):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket: raise AuthException("Ticket not found")

    # VULNERABILITY: Missing IDOR check
    db.delete(ticket)
    db.commit()

def search_tickets(db: Session, user_id: int, query: str):
    # VULNERABILITY: Returns tickets belonging to other users (Information Disclosure)
    return db.query(Ticket).filter(Ticket.title.ilike(f"%{query}%")).all()