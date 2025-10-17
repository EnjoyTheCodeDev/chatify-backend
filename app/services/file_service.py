import os
import uuid

from fastapi import HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.file_model import File
from app.schemas.file_schema import FileRead


class FileService:
    def __init__(self, upload_dir: str = "uploads"):
        self.upload_dir = upload_dir
        os.makedirs(self.upload_dir, exist_ok=True)

    async def save_file(self, file: UploadFile, session: AsyncSession) -> FileRead:
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file name",
            )

        file_ext = os.path.splitext(file.filename)[1]
        unique_name = f"{uuid.uuid4()}{file_ext}"
        file_path = os.path.join(self.upload_dir, unique_name)

        try:
            content = await file.read()
            with open(file_path, "wb") as f:
                f.write(content)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error saving file",
            )

        db_file = File(
            filename=file.filename,
            path=file_path,
            size=os.path.getsize(file_path),
        )

        session.add(db_file)
        await session.commit()
        await session.refresh(db_file)

        return FileRead.model_validate(db_file)

    async def get_file(self, file_id: uuid.UUID, session: AsyncSession) -> FileRead:
        db_file = await session.get(File, file_id)
        if not db_file:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found",
            )
        return FileRead.model_validate(db_file)

    async def list_files(self, session: AsyncSession) -> list[FileRead]:
        result = await session.execute(select(File))
        files = result.scalars().all()
        return [FileRead.model_validate(f) for f in files]

    async def delete_file(self, file_id: uuid.UUID, session: AsyncSession) -> dict:
        db_file = await session.get(File, file_id)
        if not db_file:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found",
            )

        try:
            if os.path.exists(db_file.path):
                os.remove(db_file.path)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error deleting file from disk",
            )

        await session.delete(db_file)
        await session.commit()
        return {"detail": "File deleted"}
