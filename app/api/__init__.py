from fastapi import APIRouter

from .routes.auth_router import router as auth_router
from .routes.chat_router import router as chat_router
from .routes.message_router import router as message_router
from .routes.user_router import router as user_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(chat_router)
api_router.include_router(message_router)
api_router.include_router(user_router)
