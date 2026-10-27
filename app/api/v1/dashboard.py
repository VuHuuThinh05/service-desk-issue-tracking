
from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.ticket import Ticket
from app.models.user import User
from app.schemas.dashboard import DashboardSummary


router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary", response_model=DashboardSummary)
def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DashboardSummary:
    total = db.scalar(select(func.count()).select_from(Ticket)) or 0

    status_counts = dict(
        db.execute(
            select(Ticket.status, func.count())
            .group_by(Ticket.status)
        ).all()
    )

    priority_counts = dict(
        db.execute(
            select(Ticket.priority, func.count())
            .group_by(Ticket.priority)
        ).all()
    )

    if current_user.role == "EMPLOYEE":
        employee_tickets = select(Ticket).where(
            Ticket.requester_id == current_user.id
        ).subquery()

        total = db.scalar(
            select(func.count()).select_from(employee_tickets)
        ) or 0

        status_counts = dict(
            db.execute(
                select(employee_tickets.c.status, func.count())
                .group_by(employee_tickets.c.status)
            ).all()
        )

        priority_counts = dict(
            db.execute(
                select(employee_tickets.c.priority, func.count())
                .group_by(employee_tickets.c.priority)
            ).all()
        )

    elif current_user.role == "SUPPORT_AGENT":
        agent_tickets = select(Ticket).where(
            Ticket.assignee_id == current_user.id
        ).subquery()

        total = db.scalar(
            select(func.count()).select_from(agent_tickets)
        ) or 0

        status_counts = dict(
            db.execute(
                select(agent_tickets.c.status, func.count())
                .group_by(agent_tickets.c.status)
            ).all()
        )

        priority_counts = dict(
            db.execute(
                select(agent_tickets.c.priority, func.count())
                .group_by(agent_tickets.c.priority)
            ).all()
        )

    return DashboardSummary(
        total_tickets=total,
        open_tickets=status_counts.get("OPEN", 0),
        in_progress_tickets=status_counts.get("IN_PROGRESS", 0),
        resolved_tickets=status_counts.get("RESOLVED", 0),
        closed_tickets=status_counts.get("CLOSED", 0),
        urgent_tickets=priority_counts.get("URGENT", 0),
        high_priority_tickets=priority_counts.get("HIGH", 0),
    )
