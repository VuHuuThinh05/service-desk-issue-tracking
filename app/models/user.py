import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, CheckConstraint, DateTime, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.comment import Comment
    from app.models.ticket import Ticket
    from app.models.ticket_event import TicketEvent


class User(Base):
    __tablename__ = "users"

    __table_args__ = (
        CheckConstraint(
            "role IN ('EMPLOYEE', 'SUPPORT_AGENT', 'ADMIN')",
            name="ck_users_role",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )
    password_hash: Mapped[str] = mapped_column(nullable=False)
    role: Mapped[str] = mapped_column(String(30), nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default="true",
        nullable=False,
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

    requested_tickets: Mapped[list["Ticket"]] = relationship(
        back_populates="requester",
        foreign_keys="Ticket.requester_id",
    )
    assigned_tickets: Mapped[list["Ticket"]] = relationship(
        back_populates="assignee",
        foreign_keys="Ticket.assignee_id",
    )
    comments: Mapped[list["Comment"]] = relationship(
        back_populates="author",
    )
    events: Mapped[list["TicketEvent"]] = relationship(
        back_populates="actor",
    )