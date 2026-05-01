from sqlalchemy.orm import Session
from app.exceptions import AuthException
from app.models import Ticket, TicketSeverity, TicketStatus, User, UserRole
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
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise AuthException("User not found")
        
    if user.role in [UserRole.MANAGER, UserRole.ADMIN]:
        return db.query(Ticket).all()
        
    return db.query(Ticket).filter(Ticket.owner_id == user_id).all()

def get_ticket(db: Session, user_id: int, ticket_id: int, client_ip: str):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket: raise AuthException("Ticket not found")

    # IDOR Prevention (Access Control Check)
    if ticket.owner_id != user_id:
        raise AuthException("Access denied: You don't own this ticket")
        
    return ticket

def update_ticket(db: Session, user_id: int, ticket_id: int, request, client_ip: str):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket: raise AuthException("Ticket not found")

    # IDOR Prevention
    if ticket.owner_id != user_id:
        raise AuthException("Access denied: You don't own this ticket")

    if request.title is not None: ticket.title = request.title
    if request.description is not None: ticket.description = request.description
    if request.severity is not None: ticket.severity = request.severity

    db.commit()
    db.refresh(ticket)
    return ticket

def delete_ticket(db: Session, user_id: int, ticket_id: int, client_ip: str):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket: raise AuthException("Ticket not found")

    # IDOR Prevention
    if ticket.owner_id != user_id:
        raise AuthException("Access denied: You don't own this ticket")

    db.delete(ticket)
    db.commit()

def search_tickets(db: Session, user_id: int, query: str):
    tickets = db.query(Ticket).filter(Ticket.title.ilike(f"%{query}%")).all()
    
    return [ticket for ticket in tickets if ticket.owner_id == user_id]