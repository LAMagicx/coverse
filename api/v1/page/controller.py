from fastapi import Request, APIRouter, status
from fastapi.responses import JSONResponse
from typing import List

from v1.common.schemas import (
    Page,
    FetchPage,
    FetchPages,
    PageQuery,
    PageQueries,
    ParentPage,
    ParentPages,
)
from v1.common.limiter import limiter
from .service import PageService

service = PageService()
router = APIRouter()


@router.post("/")
@limiter.limit("1/minute")
async def upload_pages(pages: List[Page], request: Request):
    """POST /pages/ - create pages"""
    created_pages = []
    for page in pages:
        created_page = await service.create_page(page)
        created_pages.append(created_page)
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_pages)


@router.post("/{page_id}")
@limiter.limit("1/minute")
async def upload_page(page_id: int, page: Page, request: Request):
    """POST /pages/{page_id} - create page with id"""
    page.id = page_id
    res = await service.create_page(page)
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=res)


@router.get("/")
@limiter.limit("1/minute")
async def get_pages(request: Request) -> List[FetchPage]:
    """GET /pages/ - fetch all pages"""
    pages = await service.fetch_all_pages()
    return JSONResponse(
        status_code=status.HTTP_200_OK, content=[page.dict() for page in pages]
    )


@router.get("/{page_id}")
@limiter.limit("1/minute")
async def get_page(page_id: int, request: Request) -> FetchPage:
    """GET /pages/ - fetch a page from id"""
    page = await service.fetch_page(page_id=page_id)
    return JSONResponse(status_code=status.HTTP_200_OK, content=page.dict())


@router.delete("/{page_id}")
@limiter.limit("1/minute")
async def delete_page(page_id: int, request: Request) -> dict:
    """DELETE /pages/{page_id} - delete a page from id
    should be only run by admin"""
    page = await service.delete_page(page_id=page_id)
    return JSONResponse(status_code=status.HTTP_202_ACCEPTED, content=page.dict())


@router.get("/search-text/{query}")
@limiter.limit("1/minute")
async def search_pages(query: str, request: Request) -> List[PageQuery]:
    """GET /pages/search/{query} - queries pages and returns close pages"""
    pages = await service.search_pages(query)
    return JSONResponse(
        status_code=status.HTTP_200_OK, content=[page for page in pages]
    )


@router.get("/search-semantic/{query}")
@limiter.limit("1/minute")
async def search_pages(query: str, request: Request) -> List[PageQuery]:
    """GET /pages/search/{query} - queries pages and returns close pages"""
    pages = await service.semantic_search_pages(query)
    return JSONResponse(
        status_code=status.HTTP_200_OK, content=[page for page in pages]
    )


@router.get("/parent/{page_id}")
@limiter.limit("1/minute")
async def find_parent_pages(page_id: int) -> List[ParentPage]:
    """GET /pages/parent/{page_id} - find pages that point to search page"""
    parents = await service.find_parent_pages(page_id)
    return JSONResponse(
        status_code=status.HTTP_200_OK, content=[parent for parent in parents]
    )
