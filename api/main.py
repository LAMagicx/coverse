# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from v1.common.loggers import create_logger
logger = create_logger(__name__)

from v1.api import router as api_router
from v1.api import auth_handler


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.auth = auth_handler
    yield

api = FastAPI(lifespan=lifespan)

api.logger = logger

api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


api.include_router(api_router, prefix="/api/v1")
