# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from api_v1.api import auth_handler
from api_v1.api import router as api_router
from db import Database

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.db = Database()
    app.auth = auth_handler
    yield
    await app.db.close()

api = FastAPI(lifespan=lifespan)

api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@api.get("/")
async def root():
    return {"message": "Hello World!"}

api.include_router(api_router, prefix="/api/v1")
