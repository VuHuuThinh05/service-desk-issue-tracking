import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.comment import Comment
    from app.models.ticket_event import TicketEvent
    from app.models.user import User


class Ticket(Base):
    __tablename__ = "tickets"

    __table_args__ = (
        CheckConstraint(
            "priority IN ('LOW', 'MEDIUM', 'HIGH', 'URGENT')",
            name="ck_tickets_priority",
        ),
        CheckConstraint(
            "status IN ('OPEN', 'IN_PROGRESS', 'RESOLVED', 'CLOSED')",
            name="ck_tickets_status",
        ),
        Index("ix_tickets_requester_id", "requester_id"),
        Index("ix_tickets_assignee_id", "assignee_id"),
        Index("ix_tickets_status", "status"),
        Index("ix_tickets_created_at", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    ticket_number: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    priority: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20),
        default="OPEN",
        server_default="OPEN",
        nullable=False,
    )
    requester_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )
    assignee_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    closed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    requester: Mapped["User"] = relationship(
        back_populates="requested_tickets",
        foreign_keys=[requester_id],
    )
    assignee: Mapped["User | None"] = relationship(
        back_populates="assigned_tickets",
        foreign_keys=[assignee_id],
    )
    comments: Mapped[list["Comment"]] = relationship(
        back_populates="ticket",
    )
    events: Mapped[list["TicketEvent"]] = relationship(
        back_populates="ticket",
    )