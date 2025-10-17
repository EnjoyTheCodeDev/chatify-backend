from app.core.database import get_session
from app.core.security import JWTService
from app.schemas.auth_schema import Token, UserCreate, UserLogin
from app.services.auth_service import AuthService
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/auth", tags=["Auth"])

jwt_service = JWTService(secret_key="supersecretkey")
auth_service = AuthService(jwt_service=jwt_service)


@router.post("/signup", response_model=Token)
async def register_user(data: UserCreate, session: AsyncSession = Depends(get_session)):
    access_token = await auth_service.signup_user(data, session)
    return Token(access_token=access_token)


@router.post("/login", response_model=Token)
async def login_user(data: UserLogin, session: AsyncSession = Depends(get_session)):
    access_token = await auth_service.login_user(data, session)
    return Token(access_token=access_token)
