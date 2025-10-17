import uuid
from typing import List, Optional

from pydantic import Field

from .base_schema import BaseModel
from .user_schema import UserRead


class ChatCreate(BaseModel):
    receiver_id: uuid.UUID = Field(..., description="ID of the user to chat with")


class ChatRead(BaseModel):
    id: uuid.UUID
    creator_id: uuid.UUID
    users: List[UserRead]
    last_message: Optional[str] = None

    class Config:
        from_attributes = True
