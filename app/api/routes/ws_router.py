from uuid import UUID

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

from app.core.dependencies import get_current_user_ws
from app.models.user_model import User
from app.services.ws_service import ws_service

router = APIRouter(prefix="/ws", tags=["WebSocket"])


@router.websocket("/chats/{chat_id}")
async def websocket_chat(
    websocket: WebSocket,
    chat_id: UUID,
    user: User = Depends(get_current_user_ws),
):
    await ws_service.connect(chat_id, websocket)

    try:
        while True:
            await websocket.receive_json()

    except WebSocketDisconnect:
        await ws_service.disconnect(chat_id, websocket)
