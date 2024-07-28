from v1.db import DatabaseController
from v1.common.schemas import Command, FetchCommands

class CommandRepository(DatabaseController):

    def __init__(self):
        super().__init__()

    async def fetch_page_command_limits(self, page_id: int):
        """ fetch page commands from the page id """
        select_query = f"SELECT limit, commands.name FROM page:{page_id};"
        data = await anext(self.sql(select_query))
        print(data)
        if data:
            return data
        else:
            return None

    async def create_command(self, page_id: int, command:Command):
        """ creates as new command """
        command_id = f"page_{page_id}_" + command.name.replace(' ', '_').lower()
        create_query = f"""CREATE ONLY 'command:{command_id}' SET name="{command.name}", text="{command.text}", page=page:{command.page}, required=[{','.join([f"'page:{page_id}'" for page_id in command.required])}];\n"""
        create_query += f"""UPDATE page:{page_id} SET commands += 'command:{command_id}';"""
        data = await anext(self.sql(create_query))
        print(data)
        if data:
            return data
        else:
            return None

