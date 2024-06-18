# api_v1/api.py

from fastapi import APIRouter, Request, Depends

from .endpoints import pages, auth, page
from .auth import AuthHandler

auth_handler = AuthHandler()

router = APIRouter()
router.include_router(auth.router, prefix="/auth", tags=["Auth"])
router.include_router(pages.router, prefix="/pages", tags=["Pages"])
router.include_router(page.router, prefix="/page", dependencies=[Depends(auth_handler.auth_wrapper)], tags=["Pages"])
