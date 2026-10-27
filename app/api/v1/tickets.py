from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.comment import Comment
from app.models.ticket import Ticket
from app.models.ticket_event import TicketEvent
from app.models.user import User
from app.schemas.ticket import (
    CommentCreate,
    CommentRead,
    TicketAssign,
    TicketCreate,
    TicketEventRead,
    TicketRead,
    TicketTransition,
)
from app.services.ticket_service import (
    assign_ticket,
    create_ticket,
    ensure_ticket_access,
    get_ticket_or_404,
    record_event,
    transition_ticket,
)


router = APIRouter(prefix="/tickets", tags=["Quản lý ticket"])


def visible_tickets_query(user: User):
    query = select(Ticket)

    if user.role == "EMPLOYEE":
        query = query.where(Ticket.requester_id == user.id)

    elif user.role == "SUPPORT_AGENT":
        query = query.where(Ticket.assignee_id == user.id)

    elif user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vai trò không được phép xem ticket.",
        )

    return query


@router.post(
    "",
    response_model=TicketRead,
    status_code=status.HTTP_201_CREATED,
)
def create_ticket_endpoint(
    payload: TicketCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_ticket(db, current_user, payload)


@router.get("", response_model=list[TicketRead])
def list_tickets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    ticket_status: str | None = Query(default=None, alias="status"),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    query = visible_tickets_query(current_user)

    if ticket_status is not None:
        allowed_statuses = {
            "OPEN", "IN_PROGRESS", "RESOLVED", "CLOSED"
        }
        if ticket_status not in allowed_statuses:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Bộ lọc trạng thái không hợp lệ.",
            )
        query = query.where(Ticket.status == ticket_status)

    from sqlalchemy import case, select
    query = query.offset(offset).limit(limit)

    return list(db.scalars(query).all())


@router.get("/{ticket_id}", response_model=TicketRead)
def get_ticket(
    ticket_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ticket = get_ticket_or_404(db, ticket_id)
    ensure_ticket_access(ticket, current_user)
    return ticket


@router.post("/{ticket_id}/assign", response_model=TicketRead)
def assign_ticket_endpoint(
    ticket_id: UUID,
    payload: TicketAssign,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ticket = get_ticket_or_404(db, ticket_id)
    return assign_ticket(
        db,
        ticket,
        current_user,
        payload.assignee_id,
    )


@router.post(
    "/{ticket_id}/transitions",
    response_model=TicketRead,
)
def transition_ticket_endpoint(
    ticket_id: UUID,
    payload: TicketTransition,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ticket = get_ticket_or_404(db, ticket_id)
    return transition_ticket(
        db,
        ticket,
        current_user,
        payload.status,
    )


@router.get(
    "/{ticket_id}/comments",
    response_model=list[CommentRead],
)
def list_comments(
    ticket_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ticket = get_ticket_or_404(db, ticket_id)
    ensure_ticket_access(ticket, current_user)

    query = (
        select(Comment)
        .where(Comment.ticket_id == ticket_id)
        .order_by(Comment.created_at.asc())
    )
    return list(db.scalars(query).all())


@router.post(
    "/{ticket_id}/comments",
    response_model=CommentRead,
    status_code=status.HTTP_201_CREATED,
)
def create_comment(
    ticket_id: UUID,
    payload: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ticket = get_ticket_or_404(db, ticket_id)
    ensure_ticket_access(ticket, current_user)

    if ticket.status == "CLOSED":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Không thể bình luận trên ticket đã đóng.",
        )

    comment = Comment(
        ticket_id=ticket.id,
        author_id=current_user.id,
        body=payload.body,
    )

    try:
        db.add(comment)
        db.flush()

        record_event(
            db,
            ticket,
            current_user,
            "COMMENT_ADDED",
            None,
            {"comment_id": str(comment.id)},
        )

        db.commit()
        db.refresh(comment)
        return comment

    except Exception:
        db.rollback()
        raise


@router.get(
    "/{ticket_id}/events",
    response_model=list[TicketEventRead],
)
def list_ticket_events(
    ticket_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ticket = get_ticket_or_404(db, ticket_id)
    ensure_ticket_access(ticket, current_user)

    query = (
        select(TicketEvent)
        .where(TicketEvent.ticket_id == ticket_id)
        .order_by(TicketEvent.created_at.asc())
    )
    return list(db.scalars(query).all())