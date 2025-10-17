from app.core.security import JWTService
from app.models.user_model import User
from app.schemas.auth_schema import UserCreate, UserLogin
from fastapi import HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession


class AuthService:
    def __init__(self, jwt_service: JWTService):
        self.jwt_service = jwt_service

    async def signup_user(self, data: UserCreate, session: AsyncSession) -> str:
        existing = await session.execute(
            select(User).where(
                or_(User.email == data.email, User.nickname == data.nickname)
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email or nickname already exists",
            )

        user = User(
            email=data.email,
            nickname=data.nickname,
            password_hash=self.jwt_service.get_password_hash(data.password),
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

        token = self.jwt_service.create_access_token({"sub": str(user.id)})
        return token

    async def login_user(self, data: UserLogin, session: AsyncSession) -> str:
        result = await session.execute(
            select(User).where(
                or_(User.email == data.login, User.nickname == data.login)
            )
        )
        user = result.scalar_one_or_none()

        if not user or not self.jwt_service.verify_password(
            data.password, user.password_hash
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )

        token = self.jwt_service.create_access_token({"sub": str(user.id)})
        return token
