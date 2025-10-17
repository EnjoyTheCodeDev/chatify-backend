import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.dependencies import get_current_user
from app.models.user_model import User
from app.schemas.message_schema import MessageCreate, MessageRead
from app.services.file_service import FileService
from app.services.message_service import MessageService
from app.services.ws_service import ws_service

router = APIRouter(
    prefix="/messages",
    tags=["Messages"],
    dependencies=[Depends(get_current_user)],
)

file_service = FileService()
message_service = MessageService(file_service)


@router.post("/", response_model=MessageRead, status_code=status.HTTP_201_CREATED)
async def send_message(
    chat_id: uuid.UUID = Form(...),
    content: Optional[str] = Form(None),
    files: Optional[List[UploadFile]] = File(None),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    message = await message_service.send_message(
        data=MessageCreate(chat_id=chat_id, content=content, file_ids=None),
        author_id=current_user.id,
        session=session,
        files=files,
    )

    await ws_service.broadcast(chat_id, {"type": "NEW_MESSAGE"})
    return message


@router.get("/chat/{chat_id}", response_model=list[MessageRead])
async def get_chat_messages(
    chat_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
):
    return await message_service.get_chat_messages(chat_id, session)


@router.put("/{message_id}", response_model=MessageRead)
async def update_message(
    message_id: uuid.UUID,
    content: str = Form(...),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    return await message_service.update_message(
        message_id=message_id,
        author_id=current_user.id,
        content=content,
        session=session,
    )


@router.delete("/{message_id}", status_code=status.HTTP_200_OK)
async def delete_message(
    message_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    return await message_service.delete_message(
        message_id=message_id,
        author_id=current_user.id,
        session=session,
    )
