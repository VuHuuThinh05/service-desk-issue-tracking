import uuid
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.ticket import Ticket
from app.models.ticket_event import TicketEvent
from app.models.user import User


VALID_PRIORITIES = {"LOW", "MEDIUM", "HIGH", "URGENT"}

VALID_TRANSITIONS = {
    "OPEN": {"IN_PROGRESS"},
    "IN_PROGRESS": {"RESOLVED"},
    "RESOLVED": {"IN_PROGRESS", "CLOSED"},
    "CLOSED": set(),
}


def record_event(
    db: Session,
    ticket: Ticket,
    actor: User,
    event_type: str,
    old_value: dict | None,
    new_value: dict | None,
) -> None:
    db.add(
        TicketEvent(
            ticket_id=ticket.id,
            actor_id=actor.id,
            event_type=event_type,
            old_value=old_value,
            new_value=new_value,
        )
    )


def get_ticket_or_404(db: Session, ticket_id: uuid.UUID) -> Ticket:
    ticket = db.get(Ticket, ticket_id)

    if ticket is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy ticket.",
        )

    return ticket


def ensure_ticket_access(ticket: Ticket, user: User) -> None:
    if user.role == "ADMIN":
        return

    if user.role == "EMPLOYEE" and ticket.requester_id == user.id:
        return

    if user.role == "SUPPORT_AGENT" and ticket.assignee_id == user.id:
        return

    # Dùng cùng một phản hồi cho ticket không tồn tại và ticket
    # người dùng không có quyền xem để hạn chế dò tìm dữ liệu.
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Không tìm thấy ticket.",
    )


def create_ticket(
    db: Session,
    actor: User,
    data,
) -> Ticket:
    if actor.role not in {"EMPLOYEE", "ADMIN"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vai trò này không được phép tạo ticket.",
        )   
    if data.priority not in VALID_PRIORITIES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Mức ưu tiên không hợp lệ.",
        )

    ticket = Ticket(
        ticket_number=f"SD-{uuid.uuid4().hex[:10].upper()}",
        title=data.title,
        description=data.description,
        category=data.category,
        priority=data.priority,
        status="OPEN",
        requester_id=actor.id,
    )

    try:
        db.add(ticket)
        db.flush()

        record_event(
            db,
            ticket,
            actor,
            "TICKET_CREATED",
            None,
            {
                "status": "OPEN",
                "priority": data.priority,
                "requester_id": str(actor.id),
            },
        )

        db.commit()
        db.refresh(ticket)
        return ticket

    except Exception:
        db.rollback()
        raise



def assign_ticket(
    db: Session,
    ticket: Ticket,
    actor: User,
    assignee_id: uuid.UUID,
) -> Ticket:
    if actor.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ Admin được phân công ticket.",
        )

    assignee = db.get(User, assignee_id)

    if (
        assignee is None
        or not assignee.is_active
        or assignee.role != "SUPPORT_AGENT"
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Người được giao phải là Support Agent đang hoạt động.",
        )

    if ticket.status == "CLOSED":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Không thể phân công ticket đã đóng.",
        )

    old_assignee = (
        str(ticket.assignee_id) if ticket.assignee_id else None
    )
    old_status = ticket.status

    ticket.assignee_id = assignee.id

    if ticket.status == "OPEN":
        ticket.status = "IN_PROGRESS"

    try:
        record_event(
            db,
            ticket,
            actor,
            "TICKET_ASSIGNED",
            {"assignee_id": old_assignee},
            {"assignee_id": str(assignee.id)},
        )

        if old_status != ticket.status:
            record_event(
                db,
                ticket,
                actor,
                "STATUS_CHANGED",
                {"status": old_status},
                {"status": ticket.status},
            )

        db.commit()
        db.refresh(ticket)
        return ticket

    except Exception:
        db.rollback()
        raise


def transition_ticket(
    db: Session,
    ticket: Ticket,
    actor: User,
    new_status: str,
) -> Ticket:
    if actor.role != "SUPPORT_AGENT":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ Support Agent được chuyển trạng thái ticket.",
        )

    if ticket.assignee_id != actor.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn chỉ được xử lý ticket đã được giao cho mình.",
        )

    if new_status not in VALID_TRANSITIONS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Trạng thái không hợp lệ.",
        )

    old_status = ticket.status

    if new_status not in VALID_TRANSITIONS[old_status]:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Không thể chuyển từ {old_status} sang {new_status}.",
        )

    now = datetime.now(timezone.utc)
    ticket.status = new_status

    if new_status == "RESOLVED":
        ticket.resolved_at = now
    elif new_status == "CLOSED":
        ticket.closed_at = now
    elif new_status == "IN_PROGRESS":
        ticket.resolved_at = None

    try:
        record_event(
            db,
            ticket,
            actor,
            "STATUS_CHANGED",
            {"status": old_status},
            {"status": new_status},
        )

        db.commit()
        db.refresh(ticket)
        return ticket

    except Exception:
        db.rollback()
        raise