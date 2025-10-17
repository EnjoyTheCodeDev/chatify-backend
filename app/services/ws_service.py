from typing import Dict, List, Optional
from uuid import UUID

from fastapi import WebSocket


class SocketService:
    def __init__(self):
        self.connections: Dict[UUID, List[WebSocket]] = {}

    async def connect(self, chat_id: UUID, websocket: WebSocket):
        await websocket.accept()
        if chat_id not in self.connections:
            self.connections[chat_id] = []
        self.connections[chat_id].append(websocket)
        print(
            f">>> User connected to chat {chat_id}, total: {len(self.connections[chat_id])}"
        )

    async def disconnect(self, chat_id: UUID, websocket: WebSocket):
        print(f">>> Disconnecting from chat {chat_id}")
        if chat_id in self.connections:
            if websocket in self.connections[chat_id]:
                self.connections[chat_id].remove(websocket)
                try:
                    await websocket.close()
                except Exception as e:
                    print(f">>> Error while closing WS: {e}")
            if not self.connections[chat_id]:
                del self.connections[chat_id]
        print(
            f">>> Remaining connections for chat {chat_id}: {len(self.connections.get(chat_id, []))}"
        )

    async def broadcast(
        self, chat_id: UUID, message: dict, sender: Optional[WebSocket] = None
    ):
        print(f">>> Broadcasting message to chat {chat_id}")
        if chat_id not in self.connections:
            return

        for connection in list(self.connections[chat_id]):
            if connection != sender:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    print(f">>> Error sending WS message: {e}")
                    await self.disconnect(chat_id, connection)


ws_service = SocketService()
