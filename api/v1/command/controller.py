from fastapi import Request, APIRouter, status
from fastapi.responses import JSONResponse
from typing import List

from v1.common.schemas import Command, FetchCommands
from .service import CommandService

service = CommandService()
router = APIRouter()

@router.post('/{page_id}')
async def upload_command(page_id: int, command: Command, request: Request):
    """ POST /commands/{page_id} - create command on page id """
    created_command = await service.create_command(page_id, command)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=created_command
    )

