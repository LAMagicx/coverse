# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

from v1.common.loggers import create_logger
from v1.common.limiter import limiter

from v1.api import router as api_router
from v1.api import auth_handler


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.auth = auth_handler
    yield


api = FastAPI(lifespan=lifespan)

api.state.limiter = limiter
api.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

logger = create_logger(__name__)
api.logger = logger

api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


api.include_router(api_router, prefix="/api/v1")
