from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_model import User


class UserService:
    async def get_all_users(self, session: AsyncSession):
        result = await session.execute(select(User))
        return result.scalars().all()
