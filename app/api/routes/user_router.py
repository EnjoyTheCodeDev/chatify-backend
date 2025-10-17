from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.dependencies import get_current_user
from app.schemas.user_schema import UserRead
from app.services.user_service import UserService

router = APIRouter(
    prefix="/users", tags=["users"], dependencies=[Depends(get_current_user)]
)


@router.get("/", response_model=list[UserRead], status_code=200)
async def get_all_users(session: AsyncSession = Depends(get_session)):
    return await UserService().get_all_users(session)


@router.get("/me", response_model=UserRead, status_code=200)
async def get_current_user_info(current_user: UserRead = Depends(get_current_user)):
    return current_user
