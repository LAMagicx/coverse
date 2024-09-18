from typing import Annotated, List
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.text import Text
from rich import print_json
from async_typer import AsyncTyper
import typer
import json
import readline

from utils.schema import Page, Command, Pages, CreatePage, CreateCommands
from utils.db import make_request

err_console = Console(stderr=True)
console = Console()
app = AsyncTyper()


def post_command(page_id: int, command: Command):
    res = make_request("POST", f"/v1/commands/{page_id}", data=command.model_dump())
    if res.status_code == 201:
        console.print(f"[green]Command {command.name} successfully created.[/green]")
    elif res.status_code == 409:
        console.print(f"[red]Command {command.name} exists already.[/red]")
    elif res.status_code == 423:
        console.print(f"[red]Page {page_id} command limit reached.[/red]")
    else:
        console.print(f"[red]Command {command.name} failed to create.[/red]")


def post_page(page: CreatePage):
    res = make_request("POST", f"/v1/pages/{page.id}", data=page.model_dump())
    if res.status_code == 201:
        console.print(f"[green]Page {page.id} successfully created.[/green]")
    elif res.status_code == 409:
        console.print(f"[red]Page {page.id} exists already.[/red]")
    else:
        console.print(f"[red]Page {page.id} failed to create.[/red]")


async def fetch_page_ids() -> List[int]:
    """fetches all the page ids"""
    res = make_request("GET", "/v1/pages/")
    if res.status_code == 200:
        data = json.loads(res.content)
        return [0] + [int(p["id"].split(":")[1]) for p in data if p["id"] != "page:0"]
    else:
        return [0]


async def autocomplete_page(incomplete: str = "") -> List[int]:
    """fetches the next 3 page id possible"""
    res = make_request("GET", "/v1/sql/", params={"query": "select id from page;"})
    if res.status_code == 200:
        data = json.loads(res.content)[0]["result"]
        if data:
            # ids = [int(p['id'].split(':')[1]) for p in data]
            max_id = int(
                max(data, key=lambda p: int(p["id"].split(":")[1]))["id"].split(":")[1]
            )
            return [max_id + 1, max_id + 2, max_id + 3]
    return [0, 1, 2]


# async def page(id: Annotated[int, typer.Option(help="The id of the page", autocompletion=autocomplete_page)] = -1,
#                title: Annotated[str, typer.Option(help="The title of the page")] = "",
#                text: Annotated[str, typer.Option(help="The text of the page")] = "",
#                commands: Annotated[List[Command], typer.Option(help="Commands linked to this page, ex: {\"name\":\"command_name\", \"text\":\"command_text\", \"page\":id_of_next_page}")] = [],
#                pages: Annotated[List[Page], typer.Option(help="Json of the page to create.")] = []):
@app.async_command("page")
async def create_page(
    pages: Annotated[
        str, typer.Option(help="JSON string of the pages to create.")
    ] = "",
    id: Annotated[int, typer.Option(help="Id of the page to create.")] = -1,
):
    """Attempts to create a page with the given arguments"""
    if pages == "":
        pages = []
        if id == -1:
            # pages not set, create one page
            possible_ids = [str(i) for i in await autocomplete_page()]
            id = int(
                Prompt.ask(
                    "Enter the page id ", choices=possible_ids, default=possible_ids[0]
                )
            )

        # print pages + commands that point to this id. limit 5

        title = Prompt.ask("Enter the page title ")
        text = Prompt.ask("Enter the page text ")
        limit = max(
            1,
            min(
                9,
                int(
                    Prompt.ask(
                        "Enter the maximum number of commands (default is 6, capped at 9) "
                    )
                ),
            ),
        )
        commands = []
        while len(commands) < limit and Confirm.ask("Create Command ?"):
            name = Prompt.ask("Command name ")
            text = Prompt.ask("Command text ")
            # print possible pages to point to.
            page = Prompt.ask("Command page ")
            while not page.isdigit():
                console.print("[red]Please enter a valid page id.[/]")
                page = Prompt.ask("Command page ")

            commands.append({"name": name, "text": text, "page": page})
        pages.append(
            {
                "id": id,
                "title": title,
                "text": text,
                "commands": commands,
                "limit": limit,
            }
        )
        pages = Pages.validate_python(pages)
    else:
        pages = Pages.validate_json(pages)

    for page in pages:
        post_page(page)

    if Confirm.ask("Would you like to create another page ?"):
        await create_page()


@app.async_command("command")
async def create_command(
    commands: Annotated[
        str, typer.Option(help="JSON string of the commands to create.")
    ] = "",
    page_id: Annotated[
        int, typer.Option(help="Id of the page to add the commands.")
    ] = -1,
):
    """Attempts to create the commands given."""
    page_ids = [str(i) for i in await fetch_page_ids()]
    if commands == "":
        commands = []
        if page_id == -1:
            page_id = int(
                Prompt.ask("Enter the page id ", choices=page_ids, default=page_ids[0])
            )

            name = Prompt.ask("Command name ")
            text = Prompt.ask("Command text ")
            # print possible pages to point to.
            page = Prompt.ask("Command page ")
            while not page.isdigit():
                console.print("[red]Please enter a valid page id.[/]")
                page = Prompt.ask("Command page ")

        commands.append(
            Command.model_validate({"name": name, "text": text, "page": page})
        )
    else:
        commands = CreateCommands.validate_json(commands)
        if page_id == -1:
            page_id = int(
                Prompt.ask("Enter the page id "), choices=page_ids, default=page_ids[0]
            )

    for command in commands:
        post_command(page_id, command)

    if Confirm.ask("Would you like to create another command ?"):
        await create_command()
