# api_v1/endpoints/page.py
from fastapi import APIRouter, Request, status, HTTPException
from fastapi.responses import JSONResponse
from pydantic import ValidationError, TypeAdapter
from typing import List
import json

from api_v1.schemas import CreatePage, Page
Pages = TypeAdapter(List[Page])

router = APIRouter()

async def fetch_page(page_id: int, request: Request) -> Page | None:
    """ selects one page given by the page_id """
    select_query = f"SELECT id, title, text, commands.name, commands.text, commands.page FROM page:{page_id};"
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

async def fetch_pages(request: Request) -> List[Page]:
    """ fetch pages from database """
    select_query = "SELECT id, title, text, commands.name, commands.text, commands.page FROM page;"
    try:
        conn = await request.app.db.get_connection()
        response = await conn.post('/sql', data=select_query)
        print(response.content)
        data = Pages.validate_python(json.loads(response.content)[0]['result'])
        return data
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Schema error: " + str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Oops! function fetch_pages encoutered an error: " + str(e))


def create_insert_page_sql(page: CreatePage) -> str:
    """ creates the surrealdb sql to create the page and it's commands """
    command_ids = [f"page_{page.id}_" + c.name.replace(' ', '_').lower() for c in page.commands]
    page_create = f"""CREATE ONLY page:{page.id} SET title="{page.title}", text="{page.text}", commands=[{','.join([f"'command:{c_id}'" for c_id in command_ids])}];\n"""
    for c_id, c in zip(command_ids, page.commands):
        command_create = f"""CREATE ONLY 'command:{c_id}' SET name="{c.name}", text="{c.text}", page=page:{c.page};\n"""
        page_create += command_create
    return page_create

async def create_page(page: CreatePage, request: Request) -> dict:
    """ creates a new page. new page must not be already created """
    try:
        conn = await request.app.db.get_connection()
        response = await conn.post('/sql', data=create_insert_page_sql(page))
        # select the page (index 0) to return
        created_page = json.loads(response.content)[0]['result']
        return created_page
    except Exception as e:
        raise e
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Oops! function create_page encoutered an error: " + str(e))

@router.post('/')
async def upload_pages(data: List[CreatePage], request: Request):
    """ POST /pages/ - create pages """
    pages = []
    for page in data:
        if existing_page:=await fetch_page(page.id, request):
            pages.append({"message": f"page not created: {page.id}",
                          "page": existing_page})
        else:
            created_page = await create_page(page, request)
            pages.append(created_page)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=pages
    )

@router.post('/{page_id}')
async def upload_page(page_id: int, page: CreatePage, request: Request):
    """ POST /pages/{page_id} - create page with id """
    page.id = page_id
    if existing_page := await fetch_page(page.id, request):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"message": f"Page with id:{page.id} exists already.",
                     "page": existing_page.json()})
    created_page = await create_page(page, request)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={"message": f"Page:{page_id} created successfully",
                 "page": created_page})

@router.get('/')
async def get_page(request: Request) -> List[Page]:
    """ GET /pages/ - fetch all pages """
    pages = await fetch_pages(request)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=[page.dict() for page in pages]
    )

@router.get('/{page_id}')
async def get_page(page_id: int, request: Request) -> Page:
    """ GET /pages/ - fetch a page from id """
    page = await fetch_page(page_id, request)
    if page is not None:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=page.dict()
        )
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"message": f"Could not find page with id: {page_id}",
                 "content": {"page_id": page_id}}
    )

