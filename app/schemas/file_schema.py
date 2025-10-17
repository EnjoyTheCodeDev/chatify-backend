import uuid

from pydantic import BaseModel, field_validator

BASE_URL = "http://localhost:8000"


class FileBase(BaseModel):
    filename: str
    path: str
    size: int


class FileRead(BaseModel):
    id: uuid.UUID
    filename: str
    path: str

    @field_validator("path", mode="before")
    def build_full_url(cls, path: str) -> str:
        if not path.startswith("http"):
            return f"{BASE_URL}/{path.lstrip('/')}"
        return path

    class Config:
        from_attributes = True
