# api_v1/endpoints/pages.py
from fastapi import APIRouter, Request, status
from pydantic import BaseModel, TypeAdapter, ValidationError
from typing import List
import json

from api_v1.schemas import Page

Pages = TypeAdapter(List[Page])

router = APIRouter()

@router.get("/")
async def get_pages(request: Request) -> List[Page]:
    """ fetch pages from database """
    try:
        conn = await request.app.db.get_connection()
        response = await conn.post('/sql', data="SELECT id, title, text FROM page;")
        data = Pages.validate_python(json.loads(response.content)[0]['result'])
        return data
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Schema error: " + str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Oops! function fetch_pages encoutered an error: " + str(e))
