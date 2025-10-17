import os
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseModel):
    db_url: str = os.getenv(
        "DB_URL", "postgresql://postgres:postgres@localhost:5432/postgres"
    )
    port: int = int(os.getenv("PORT", 8000))

settings = Settings()

def get_db_url() -> str:
    return settings.db_url

