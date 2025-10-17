import uuid
from typing import Optional

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base_model import Base
from .chat_model import chat_users
from .timestamp_model import TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        index=True,
        default=uuid.uuid4,
    )

    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    nickname: Mapped[Optional[str]] = mapped_column(String(50), unique=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    chats = relationship("Chat", secondary=chat_users, back_populates="users")
    messages = relationship("Message", back_populates="author", cascade="all, delete")
