from uuid import UUID

from pydantic import BaseModel


class UserRead(BaseModel):
    id: UUID
    nickname: str
    email: str

    class Config:
        from_attributes = True
