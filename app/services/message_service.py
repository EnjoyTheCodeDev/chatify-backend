import uuid
from typing import Optional

from fastapi import HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.chat_model import Chat
from app.models.file_model import File
from app.models.message_model import Message
from app.models.user_model import User
from app.schemas.message_schema import MessageCreate, MessageRead
from app.services.file_service import FileService


class MessageService:
    def __init__(self, file_service: FileService):
        self.file_service = file_service

    async def send_message(
        self,
        data: MessageCreate,
        author_id: uuid.UUID,
        session: AsyncSession,
        files: Optional[list[UploadFile]] = None,
    ) -> MessageRead:
        chat = await session.get(Chat, data.chat_id)
        user = await session.get(User, author_id)

        if not chat or not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat or user not found",
            )

        if not data.content and not files and not data.file_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Message must have content or files",
            )

        message = Message(chat=chat, author=user, content=data.content or "")

        if files:
            saved_files = []
            for file in files:
                saved = await self.file_service.save_file(file, session)
                db_file = await session.get(File, saved.id)
                saved_files.append(db_file)
            message.files = saved_files

        if data.file_ids:
            result = await session.execute(
                select(File).where(File.id.in_(data.file_ids))
            )
            message.files.extend(result.scalars().all())

        session.add(message)
        await session.commit()

        result = await session.execute(
            select(Message)
            .options(
                selectinload(Message.author),
                selectinload(Message.files),
            )
            .where(Message.id == message.id)
        )
        full_message = result.scalar_one()

        return MessageRead.model_validate(full_message)

    async def get_chat_messages(
        self, chat_id: uuid.UUID, session: AsyncSession
    ) -> list[MessageRead]:
        result = await session.execute(
            select(Message)
            .options(
                selectinload(Message.author),
                selectinload(Message.files),
            )
            .where(Message.chat_id == chat_id)
        )
        messages = result.scalars().all()
        return [MessageRead.model_validate(m) for m in messages]

    async def update_message(
        self,
        message_id: uuid.UUID,
        author_id: uuid.UUID,
        content: str,
        session: AsyncSession,
    ) -> MessageRead:
        message = await session.get(Message, message_id)
        if not message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Message not found",
            )

        if message.author_id != author_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can edit only your own messages",
            )

        message.content = content
        await session.commit()

        result = await session.execute(
            select(Message)
            .options(
                selectinload(Message.author),
                selectinload(Message.files),
            )
            .where(Message.id == message.id)
        )
        updated_message = result.scalar_one()

        return MessageRead.model_validate(updated_message)

    async def delete_message(
        self, message_id: uuid.UUID, author_id: uuid.UUID, session: AsyncSession
    ) -> dict:
        message = await session.get(Message, message_id)
        if not message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Message not found",
            )

        if message.author_id != author_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can delete only your own messages",
            )

        await session.delete(message)
        await session.commit()
        return {"detail": "Message deleted"}
