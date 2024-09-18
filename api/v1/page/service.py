from typing import List
from fastapi import status
from loguru import logger

from v1.common.exceptions import BadRequestException
from v1.common.schemas import FetchPage, FetchPages, Page, PageQueries, ParentPages
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
            logger.exception(e)
            raise BadRequestException(
                str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    async def fetch_page(self, page_id: int) -> FetchPage:
        try:
            logger.log("EVENT", f"PAGE FETCH : {page_id}")
            fetched_page = await self.repository.fetch_page(page_id=page_id)
            if fetched_page is None:
                raise BadRequestException("Page not found")
            else:
                return fetched_page
        except BadRequestException as e:
            raise e
        except Exception as e:
            logger.exception(e)
            raise BadRequestException(
                str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    async def fetch_all_pages(self) -> FetchPages:
        try:
            logger.log("EVENT", f"PAGE FETCH : ALL")
            fetched_pages = await self.repository.fetch_all_pages()
            if fetched_pages is None:
                raise BadRequestException("No pages found")
            else:
                return fetched_pages
        except BadRequestException as e:
            raise e
        except Exception as e:
            logger.exception(e)
            raise BadRequestException(str(e))

    async def create_page(self, page: Page):
        try:
            logger.log("EVENT", f"PAGE CREATE : {page.id}")
            if await self.page_exists(page.id):
                raise BadRequestException(
                    "Page already exists", status_code=status.HTTP_409_CONFLICT
                )

            created_page = await self.repository.create_page(page)
            if created_page is None:
                raise BadRequestException(
                    "Could not create page", status_code=status.HTTP_400_BAD_REQUEST
                )
            else:
                return created_page
        except BadRequestException as e:
            raise e
        except Exception as e:
            logger.exception(e)
            raise BadRequestException(
                str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    async def create_pages(self, pages: List[Page]):
        try:
            for page in pages:
                yield await self.create_page(page)
        except Exception as e:
            logger.exception(e)
            raise BadRequestException(
                str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    async def delete_page(self, page_id: int):
        try:
            logger.log("EVENT", f"PAGE DELETE : {page_id}")
            page = await self.repository.fetch_page(page_id)
            if page is None:
                raise BadRequestException("Page not found")
            else:
                res = await self.repository.delete_page(page_id)
            return page
        except BadRequestException as e:
            raise e
        except Exception as e:
            logger.exception(e)
            raise BadRequestException(
                str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    async def search_pages(self, query: str) -> PageQueries:
        try:
            logger.log("EVENT", f"PAGE TEXT SEARCH: {query}")
            pages = await self.repository.search_pages(query)
            if pages is None or pages == []:
                raise BadRequestException("No pages found")
            else:
                return pages
        except BadRequestException as e:
            raise e
        except Exception as e:
            logger.exception(e)
            raise BadRequestException(
                str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    async def semantic_search_pages(self, query: str) -> PageQueries:
        try:
            logger.log("EVENT", f"PAGE SEMANTIC SEARCH: {query}")
            pages = await self.repository.semantic_search_pages(query)
            if pages is None or pages == []:
                raise BadRequestException("No pages found")
            else:
                return pages
        except BadRequestException as e:
            raise e
        except Exception as e:
            logger.exception(e)
            raise BadRequestException(
                str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    async def find_parent_pages(self, page_id: int) -> ParentPages:
        try:
            logger.log("EVENT", f"PAGE PARENTS: {page_id}")
            parents = await self.repository.find_parent_pages(page_id)
            if parents is None or parents == []:
                raise BadRequestException("No parents found")
            else:
                return parents
        except BadRequestException as e:
            raise e
        except Exception as e:
            logger.exception(e)
            raise BadRequestException(
                str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
