# api_v1/api.py

from fastapi import APIRouter, Depends

from v1 import auth
from .page import controller as page
from .command import controller as command

auth_handler = auth.AuthHandler()

router = APIRouter()
router.include_router(auth.router, prefix="/auth", tags=["Auth"])
router.include_router(page.router, prefix="/pages", dependencies=[Depends(auth_handler.auth_wrapper)], tags=["Page"])
router.include_router(command.router, prefix="/commands", dependencies=[Depends(auth_handler.auth_wrapper)], tags=["Command"])
