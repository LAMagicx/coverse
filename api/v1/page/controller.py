from fastapi import Request, APIRouter, status
from fastapi.responses import JSONResponse
from typing import List

from v1.common.schemas import Page, FetchPage, FetchPages
from .service import PageService

service = PageService()
router = APIRouter()

@router.post('/')
async def upload_pages(pages: List[Page], request: Request):
    """ POST /pages/ - create pages """
    created_pages = []
    for page in pages:
        created_page = await service.create_page(page)
        created_pages.append(created_page)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=created_pages
    )

@router.post('/{page_id}')
async def upload_page(page_id: int, page: Page, request: Request):
    """ POST /pages/{page_id} - create page with id """
    page.id = page_id
    res = await service.create_page(page)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=res
    )

@router.get('/')
async def get_pages(request: Request) -> List[FetchPage]:
    """ GET /pages/ - fetch all pages """
    pages = await service.fetch_all_pages()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=[page.dict() for page in pages]
    )

@router.get('/{page_id}')
async def get_page(page_id: int, request: Request) -> FetchPage:
    """ GET /pages/ - fetch a page from id """
    page = await service.fetch_page(page_id=page_id)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=page.dict()
    )
