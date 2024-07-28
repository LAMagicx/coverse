from fastapi import status

from v1.common.exceptions import BadRequestException
from v1.common.schemas import Command, FetchCommands
from .repository import CommandRepository

class CommandService:

    def __init__(self):
        self.repository = CommandRepository()

    async def fetch_page_command_limits(self, page_id: int):
        try:
            # test if page exists
            fetched_data = await self.repository.fetch_page_command_limits(page_id)
            if fetched_data is None:
                raise BadRequestException("No commands for page", status_code=status.HTTP_404_NOT_FOUND)
            else:
                return fetched_data
        except Exception as e:
            raise BadRequestException(str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    async def create_command(self, page_id: int, command: Command):
        try:
            # test if page exists
            if page_commands := await self.fetch_page_command_limits(page_id):
                page_commands = page_commands[0]
            else:
                raise BadRequestException("Page doesn't exist", status_code=status.HTTP_404_NOT_FOUND)

            # check if command exists
            if command.name in page_commands["commands"]["name"]:
                raise BadRequestException("Command exists", status_code=status.HTTP_409_CONFLICT)

            # test if limit reached
            if len(page_commands["commands"]["name"]) >= int(page_commands["limit"]):
                raise BadRequestException("Page command limit reached", status_code=status.HTTP_423_LOCKED)

            created_command = await self.repository.create_command(page_id, command)
            if created_command is None:
                raise BadRequestException("Could not create command", status_code=status.HTTP_400_BAD_REQUEST)
            else:
                return created_command
        except Exception as e:
            raise BadRequestException(str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
