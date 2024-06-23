# api_v1/endpoints/commands.py
from fastapi import APIRouter, Request, status, HTTPException
from fastapi.responses import JSONResponse
from pydantic import ValidationError, TypeAdapter
from typing import List
import json

from api_v1.schemas import CreateCommand, Commands

router = APIRouter()

async def fetch_commands(page_id: int, request: Request) -> dict | None:
    """ fetch page commands from the page id """
    select_query = f"SELECT limit, commands.name FROM page:{page_id};"
    try:
        conn = await request.app.db.get_connection()
        response = await conn.post('/sql', data=select_query) 
        json_response = json.loads(response.content)[0]['result']
        if json_response:
            return json_response[0]
        return None
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Schema error: " + str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Oops! function fetch_commands encoutered an error: " + str(e))

async def create_command(page_id: int, command: CreateCommand, request: Request) -> dict:
    """ creates a new command """
    command_id = f"page_{page_id}_" + command.name.replace(' ', '_').lower()
    create_query = f"""CREATE ONLY 'command:{command_id}' SET name="{command.name}", text="{command.text}", page=page:{command.page};\n"""
    create_query += f"""UPDATE page:{page_id} SET commands += 'command:{command_id}';"""
    try:
        conn = await request.app.db.get_connection()
        response = await conn.post('/sql', data=create_query)
        # select the page (index 0) to return
        created_command = json.loads(response.content)[0]['result']
        return created_command
    except Exception as e:
        raise e
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Oops! function create_command encoutered an error: " + str(e))

@router.post('/{page_id}')
async def upload_command(page_id: int, command: CreateCommand, request: Request):
    """ POST /commands/{page_id} - create command on page id """
    page = await fetch_commands(page_id, request)
    if page is None:
        # page doesn't exist
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": f"page:{page_id} not found. Page must exist."}
        )
    elif len(page['commands']['name']) >= int(page['limit']):
        # page limit reached
        return JSONResponse(
            status_code=status.HTTP_423_LOCKED,
            content={"message": f"page:{page_id}'s command limit is reached."}
        )
    elif command.name.lower() in [n.lower() for n in page['commands']['name']]:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"message": f"command exists: {command.name}",
                     "command": command.model_dump()})
    else:
        created_command = await create_command(page_id, command, request)
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content=created_command
        )

