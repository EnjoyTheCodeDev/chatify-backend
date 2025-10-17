from typing import cast

from fastapi import Depends, HTTPException, WebSocket, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.security import JWTService
from app.models.user_model import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
jwt_service = JWTService(secret_key="supersecretkey")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt_service.decode_access_token(token)
        user_id = cast(str, payload.get("sub"))

        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await session.get(User, user_id)
    if user is None:
        raise credentials_exception

    return user


async def get_current_user_ws(
    websocket: WebSocket,
    session: AsyncSession = Depends(get_session),
) -> User:
    token = websocket.query_params.get("token")

    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        raise HTTPException(status_code=403, detail="Missing token")

    try:
        payload = jwt_service.decode_access_token(token)
        user_id = cast(str, payload.get("sub"))
        if not user_id:
            raise JWTError("Missing sub")
    except JWTError:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        raise HTTPException(status_code=403, detail="Invalid token")

    user = await session.get(User, user_id)
    if not user:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        raise HTTPException(status_code=403, detail="User not found")

    return user
