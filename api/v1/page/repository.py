from typing import Optional
from v1.db import DatabaseController
from v1.common.schemas import Page, FetchPage, FetchPages


def create_insert_page_sql(page: Page) -> str:
    """ creates the surrealdb sql to create the page and it's commands """
    command_ids = [f"page_{page.id}_" + c.name.replace(' ', '_').lower() for c in page.commands]
    page_create = f"""CREATE ONLY page:{page.id} SET title="{page.title}", text="{page.text}", limit="{page.limit}", commands=[{','.join([f"'command:{c_id}'" for c_id in command_ids])}];\n"""
    for c_id, c in zip(command_ids, page.commands):
        command_create = f"""CREATE ONLY 'command:{c_id}' SET name="{c.name}", text="{c.text}", page=page:{c.page}, required=[{','.join([f"'page:{page_id}'" for page_id in c.required])}];\n"""
        page_create += command_create
    return page_create

class PageRepository(DatabaseController):

    def __init__(self):
        super().__init__()

    async def fetch_page(self, page_id: int) -> FetchPage:
        """ selects one page given by the page_id from surreal """
        select_query = f"SELECT id, title, text, commands.name, commands.text, commands.page, commands.required FROM page:{page_id};"
        data = await anext(self.sql(select_query))
        if data:
            return FetchPage.validate(data[0])
        else:
            return None

    async def fetch_all_pages(self) -> FetchPages:
        """ fetch pages from database """
        select_query = "SELECT id, title, text, commands.name, commands.text, commands.page, commands.required FROM page;"
        data = await anext(self.sql(select_query))
        if data:
            return FetchPages.validate_python(data)
        else:
            return None

    async def create_page(self, page: Page):
        create_query = create_insert_page_sql(page)
        data = [res async for res in self.sql(create_query)]
        if data:
            return data
        else:
            return None

