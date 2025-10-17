import uuid
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.chat_model import Chat
from app.models.user_model import User
from app.schemas.chat_schema import ChatRead
from app.schemas.user_schema import UserRead


class ChatService:
    async def create_chat(
        self,
        creator: User,
        receiver_id: uuid.UUID,
        session: AsyncSession,
    ) -> ChatRead:
        if creator.id == receiver_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot create chat with yourself",
            )

        receiver = await session.get(User, receiver_id)
        if not receiver:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Receiver not found",
            )

        result = await session.execute(
            select(Chat)
            .options(selectinload(Chat.users))
            .join(Chat.users)
            .where(Chat.users.any(User.id == creator.id))
            .where(Chat.users.any(User.id == receiver_id))
        )
        existing_chat = result.scalar_one_or_none()

        if existing_chat:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Chat already exists between these users",
            )

        chat = Chat(
            creator_id=creator.id,
            users=[creator, receiver],
        )

        session.add(chat)
        await session.commit()
        await session.refresh(chat)

        return ChatRead(
            id=chat.id,
            creator_id=chat.creator_id,
            users=[UserRead.model_validate(u) for u in chat.users],
            last_message=None,
        )

    async def get_chat(self, chat_id: uuid.UUID, session: AsyncSession) -> ChatRead:
        result = await session.execute(
            select(Chat)
            .options(
                selectinload(Chat.users),
                selectinload(Chat.messages),
            )
            .where(Chat.id == chat_id)
        )
        chat = result.scalar_one_or_none()

        if not chat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat not found",
            )

        last_message = (
            sorted(chat.messages, key=lambda m: m.created_at, reverse=True)[0].content
            if chat.messages
            else None
        )

        return ChatRead(
            id=chat.id,
            creator_id=chat.creator_id,
            users=[UserRead.model_validate(u) for u in chat.users],
            last_message=last_message,
        )

    async def get_user_chats(
        self, user_id: uuid.UUID, session: AsyncSession
    ) -> List[ChatRead]:
        result = await session.execute(
            select(Chat)
            .options(
                selectinload(Chat.users),
                selectinload(Chat.messages),
            )
            .join(Chat.users)
            .where(User.id == user_id)
        )
        chats = result.scalars().unique().all()

        chat_reads: List[ChatRead] = []
        for chat in chats:
            last_message = (
                sorted(chat.messages, key=lambda m: m.created_at, reverse=True)[
                    0
                ].content
                if chat.messages
                else None
            )
            chat_reads.append(
                ChatRead(
                    id=chat.id,
                    creator_id=chat.creator_id,
                    users=[UserRead.model_validate(u) for u in chat.users],
                    last_message=last_message,
                )
            )

        return chat_reads

    async def delete_chat(self, chat_id: uuid.UUID, session: AsyncSession):
        chat = await session.get(Chat, chat_id)
        if not chat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat not found",
            )

        await session.delete(chat)
        await session.commit()
        return {"detail": "Chat deleted"}
