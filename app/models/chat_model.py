import uuid

from sqlalchemy import Column, ForeignKey, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base_model import Base
from .timestamp_model import TimestampMixin

chat_users = Table(
    "chat_users",
    Base.metadata,
    Column(
        "chat_id",
        UUID(as_uuid=True),
        ForeignKey("chats.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "user_id",
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Chat(Base, TimestampMixin):
    __tablename__ = "chats"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4
    )

    creator_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    creator = relationship("User", foreign_keys=[creator_id])
    users = relationship("User", secondary=chat_users, back_populates="chats")
    messages = relationship(
        "Message", back_populates="chat", cascade="all, delete", lazy="selectin"
    )
