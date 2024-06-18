# api_v1/endpoints/page.py
from fastapi import APIRouter, Request, status, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, TypeAdapter, ValidationError
import json

from api_v1.schemas import CreatePage, Page

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


@router.post('/')
async def create(page: CreatePage, request: Request):
    """ create a page """
    create_query = f"""
    INSERT INTO page {page.model_dump_json()};
    """
    if existing_page := await fetch_page(page.id, request):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"message": f"Page with id:{page.id} exists already.",
                     "page": existing_page.json()})
    try:
        conn = await request.app.db.get_connection()
        response = await conn.post('/sql', data=create_query)
        json_response = json.loads(response.content)[0]['result']
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={"message": "succes",
                     "page": json.dumps(json_response[0])})
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Oops! function create_page encoutered an error: " + str(e))

@router.get("/")
async def get_page(page_id: int, request: Request) -> Page:
    """ fetch a page from the database """
    return fetch_page(page_id, request)
