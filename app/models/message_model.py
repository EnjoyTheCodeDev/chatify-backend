import uuid

from sqlalchemy import Column, ForeignKey, Table, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base_model import Base
from .timestamp_model import TimestampMixin

message_files = Table(
    "message_files",
    Base.metadata,
    Column(
        "message_id",
        UUID(as_uuid=True),
        ForeignKey("messages.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "file_id",
        UUID(as_uuid=True),
        ForeignKey("files.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Message(Base, TimestampMixin):
    __tablename__ = "messages"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4
    )

    chat_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("chats.id", ondelete="CASCADE"), nullable=False
    )

    author_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    content: Mapped[str] = mapped_column(Text, nullable=False)

    chat = relationship("Chat", back_populates="messages")
    author = relationship("User", back_populates="messages")
    files = relationship(
        "File",
        secondary=message_files,
        cascade="all, delete",
    )
