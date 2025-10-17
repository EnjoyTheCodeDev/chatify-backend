import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.dependencies import get_current_user
from app.models.user_model import User
from app.schemas.chat_schema import ChatCreate, ChatRead
from app.services.chat_service import ChatService

router = APIRouter(
    prefix="/chats",
    tags=["Chats"],
)

chat_service = ChatService()


@router.post("/", response_model=ChatRead, status_code=status.HTTP_201_CREATED)
async def create_chat(
    data: ChatCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    chat = await chat_service.create_chat(
        creator=current_user,
        receiver_id=data.receiver_id,
        session=session,
    )
    return ChatRead(
        id=chat.id,
        creator_id=chat.creator_id,
        users=[u for u in chat.users],
    )


@router.get("/user", response_model=list[ChatRead])
async def get_user_chats(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    chats = await chat_service.get_user_chats(current_user.id, session)

    return chats


@router.get("/{chat_id}", response_model=ChatRead)
async def get_chat(
    chat_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
):
    chat = await chat_service.get_chat(chat_id, session)
    return ChatRead(
        id=chat.id,
        creator_id=chat.creator_id,
        users=[u for u in chat.users],
    )


@router.delete("/{chat_id}", status_code=status.HTTP_200_OK)
async def delete_chat(
    chat_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
):
    return await chat_service.delete_chat(chat_id, session)
