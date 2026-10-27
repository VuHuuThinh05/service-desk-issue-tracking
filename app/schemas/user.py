
from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    full_name: str
    email: str
    role: str
    is_active: bool
    created_at: datetime


class UserCreate(BaseModel):
    full_name: str = Field(min_length=1, max_length=120)
    email: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=8)
    role: Literal["EMPLOYEE", "SUPPORT_AGENT", "ADMIN"]


class UserStatusUpdate(BaseModel):
    is_active: bool
