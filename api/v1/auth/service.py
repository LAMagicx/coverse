# api_v1/endpoints/auth.py
import os
from fastapi import APIRouter, Request, status
from loguru import logger

from v1.common.exceptions import BadRequestException
from v1.common.schemas import AuthDetails

USERNAME = os.environ.get('USERNAME', '')
HASHED_PASSWORD = os.environ.get('HASHED_PASS')

router = APIRouter()

@router.post('/login')
def login(request: Request, auth_details: AuthDetails):
    if auth_details.username == USERNAME and request.app.auth.verify_password(auth_details.password, HASHED_PASSWORD):
        # login correct
        token = request.app.auth.encode_token(USERNAME)
        logger.log("EVENT", f"LOGIN user: {auth_details.username} - {request.client.host}")
        return { 'token': token }
    else:
        log.exception(f"LOGIN FAILED user: {auth_details.username} - {request.client.host} : bad password")
        raise BadRequestException(status_code=status.HTTP_401_UNAUTHORIZED, exception='Invalid username and/or password')
