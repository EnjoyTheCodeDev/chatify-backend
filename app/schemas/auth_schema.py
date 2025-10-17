from typing import Optional

from pydantic import EmailStr, Field

from .base_schema import BaseModel


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    nickname: str


class UserLogin(BaseModel):
    login: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: Optional[str] = None
