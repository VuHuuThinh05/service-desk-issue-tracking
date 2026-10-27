
from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class TicketCreate(BaseModel):
    title: str = Field(min_length=5, max_length=200)
    description: str = Field(min_length=10, max_length=10000)
    category: str = Field(min_length=2, max_length=50)
    priority: str = "MEDIUM"


class TicketRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    ticket_number: str
    title: str
    description: str
    category: str
    priority: str
    status: str
    requester_id: UUID
    assignee_id: UUID | None
    created_at: datetime
    updated_at: datetime
    resolved_at: datetime | None
    closed_at: datetime | None


class TicketAssign(BaseModel):
    assignee_id: UUID


class TicketTransition(BaseModel):
    status: str


class CommentCreate(BaseModel):
    body: str = Field(min_length=1, max_length=5000)


class CommentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    ticket_id: UUID
    author_id: UUID
    body: str
    created_at: datetime


class TicketEventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    ticket_id: UUID
    actor_id: UUID
    event_type: str
    old_value: dict[str, Any] | None
    new_value: dict[str, Any] | None
    created_at: datetime
