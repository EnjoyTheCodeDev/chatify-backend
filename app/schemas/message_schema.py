import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import Field

from .base_schema import BaseModel
from .file_schema import FileRead


class MessageBase(BaseModel):
    content: Optional[str] = Field(None, min_length=1)
    file_ids: Optional[List[uuid.UUID]] = None


class MessageCreate(MessageBase):
    chat_id: uuid.UUID


class Author(BaseModel):
    id: uuid.UUID
    nickname: Optional[str] = None

    class Config:
        from_attributes = True


class MessageRead(MessageBase):
    id: uuid.UUID
    chat_id: uuid.UUID
    created_at: datetime
    author: Author
    files: Optional[List[FileRead]] = []

    class Config:
        from_attributes = True


class MessageUpdate(BaseModel):
    content: str
