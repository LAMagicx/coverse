# api_v1/endpoints/page.py
from fastapi import APIRouter, Request, status, HTTPException
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from typing import List
import json

from api_v1.schemas import CreatePage, Page, Upload

router = APIRouter()

async def fetch_page(page_id: int, request: Request) -> Page | None:
    """ selects one page given by the page_id """
    select_query = f""" 
    SELECT id, title, text FROM page:{page_id};
    """
    try:
        conn = await request.app.db.get_connection()
        response = await conn.post('/sql', data=select_query) 
        json_response = json.loads(response.content)[0]['result']
        if json_response:
            data = Page.validate(json_response[0])
            return data
        return None
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Schema error: " + str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Oops! function fetch_page encoutered an error: " + str(e))


def create_insert_page_sql(page: CreatePage) -> str:
    """ creates the surrealdb sql to create the page and it's commands """
    command_ids = [f"page_{page.id}_" + c.name.replace(' ', '_').lower() for c in page.commands]
    page_create = f"""CREATE ONLY page:{page.id} SET title="{page.title}", text="{page.text}", commands=[{','.join([f"'command:{c_id}'" for c_id in command_ids])}];\n"""
    for c_id, c in zip(command_ids, page.commands):
        command_create = f"""CREATE ONLY 'command:{c_id}' SET name="{c.name}", text="{c.text}", page=page:{c.page};\n"""
        page_create += command_create
    return page_create

@router.post('/')
async def create(page: CreatePage, request: Request) -> JSONResponse:
    """ create a page """
    if existing_page := await fetch_page(page.id, request):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"message": f"Page with id:{page.id} exists already.",
                     "page": existing_page.json()})
    try:
        conn = await request.app.db.get_connection()
        response = await conn.post('/sql', data=create_insert_page_sql(page))
        # select the page (index 0) to return
        created_page = json.loads(response.content)[0]['result']
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content=created_page)
    except Exception as e:
        raise e
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Oops! function create_page encoutered an error: " + str(e))


@router.post('/upload')
async def upload(data: Upload, request: Request) -> JSONResponse:
    """ creates pages + commands based on an uploaded schema """
    pages = []
    for page in data.pages:
        created_page = await create(page, request)
        if created_page.status_code == status.HTTP_201_CREATED:
            pages.append(create_page.content)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=pages
    )

@router.get("/")
async def get_page(page_id: int, request: Request) -> Page:
    """ fetch a page from the database """
    return fetch_page(page_id, request)
