from typing import List
from fastapi import status

from v1.common.exceptions import BadRequestException
from v1.common.schemas import FetchPage, FetchPages, Page, PageQueries
from .repository import PageRepository

class PageService:

    def __init__(self):
        self.repository = PageRepository()

    async def page_exists(self, page_id: int) -> bool:
        try:
            fetched_page = await self.repository.fetch_page(page_id=page_id)
            if fetched_page is None:
                return False
            else:
                return True
        except Exception as e:
            raise BadRequestException(str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    async def fetch_page(self, page_id: int) -> FetchPage:
        try:
            fetched_page = await self.repository.fetch_page(page_id=page_id)
            if fetched_page is None:
                raise BadRequestException("Page not found")
            else:
                return fetched_page
        except Exception as e:
            raise BadRequestException(str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    async def fetch_all_pages(self) -> FetchPages:
        try:
            fetched_pages = await self.repository.fetch_all_pages()
            if fetched_pages is None:
                raise BadRequestException("No pages found")
            else:
                return fetched_pages
        except Exception as e:
            raise BadRequestException(str(e))

    async def create_page(self, page: Page):
        try:
            if await self.page_exists(page.id):
                raise BadRequestException("Page already exists", status_code=status.HTTP_409_CONFLICT)

            created_page = await self.repository.create_page(page)
            if created_page is None:
                raise BadRequestException("Could not create page", status_code=status.HTTP_400_BAD_REQUEST)
            else:
                return created_page
        except Exception as e:
            raise BadRequestException(str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    async def create_pages(self, pages: List[Page]):
        try:
            for page in pages:
                yield await self.create_page(page)
        except Exception as e:
            raise BadRequestException(str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    async def delete_page(self, page_id: int):
        try:
            page = await self.repository.fetch_page(page_id)
            if page is None:
                raise BadRequestException("Page not found")
            else:
                res = await self.repository.delete_page(page_id)
            return page
        except Exception as e:
            raise BadRequestException(str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    async def search_pages(self, query: str) -> PageQueries:
        try:
            pages = await self.repository.search_pages(query)
            if pages is None or pages == []:
                raise BadRequestException("No pages found")
            else:
                return pages
        except Exception as e:
            raise BadRequestException(str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    async def semantic_search_pages(self, query: str) -> PageQueries:
        try:
            pages = await self.repository.semantic_search_pages(query)
            if pages is None or pages == []:
                raise BadRequestException("No pages found")
            else:
                return pages
        except Exception as e:
            raise BadRequestException(str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
