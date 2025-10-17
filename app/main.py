from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .api import api_router
from .api.routes.ws_router import router as ws_router
from .core.database import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()
    print("Database connection pool closed")


app = FastAPI(lifespan=lifespan)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(api_router, prefix="/api")
app.include_router(ws_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://chatify-front-lut6.onrender.com", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
