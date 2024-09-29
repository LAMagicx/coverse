# main.py
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from contextlib import asynccontextmanager
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi import _rate_limit_exceeded_handler

from v1.common.loggers import create_logger
from v1.common.limiter import limiter
from v1.common.settings import DOMAIN

from v1.api import router as api_router
from v1.api import auth_handler


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.auth = auth_handler
    yield


api = FastAPI(lifespan=lifespan)

api.state.limiter = limiter
api.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
api.add_middleware(SlowAPIMiddleware)

logger = create_logger(__name__)
api.logger = logger

api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# api.add_middleware(
#     SessionMiddleware, secret_key="secretkey", max_age=None, domain=DOMAIN
# )


# @api.middleware("http")
# async def logging_middleware(request: Request, call_next):
#     response = Response("Internal server error", status_code=500)
#     try:
#         response: Response = await call_next(request)
#     finally:
#         print(request.client, request.session)
#     return response


@api.get("/health")
async def healthcheck():
    return {"status": "OK"}


api.include_router(api_router, prefix="/api/v1")
