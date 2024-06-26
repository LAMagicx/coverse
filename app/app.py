from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.text import Text
from typing import List
from rich import print_json
import time
import os
import yaml
import requests
from async_typer import AsyncTyper
import readline

from db import create_authenticated_session, get_page
import create
from create import create_page

CONFIG_FILE_LOCATION = ".config"

if not os.path.exists(CONFIG_FILE_LOCATION):
    open(CONFIG_FILE_LOCATION, 'a+').close()

err_console = Console(stderr=True)
console = Console()

app = AsyncTyper()
app.add_typer(create.app, name="create")

def save_to_config(vars: List[str]):
    with open(CONFIG_FILE_LOCATION, 'r') as f:
        config = yaml.load(f, Loader=yaml.FullLoader) or {}
    if "settings" not in config:
        config["settings"] = {}
    for var in vars:
        config["settings"][var] = os.environ.get(var)

    with open(CONFIG_FILE_LOCATION, "w") as f:
        yaml.dump(config, stream=f, default_flow_style=False, sort_keys=False)

def check_envs():
    vars = ["COVERSE_API_URL", "COVERSE_USERNAME", "COVERSE_PASSWORD"]
    with open(CONFIG_FILE_LOCATION, "r") as f:
        config = yaml.load(f, Loader=yaml.FullLoader) or {}

    settings = config.get("settings") or {}

    for var in vars:
        if not os.environ.get(var):
            if value := settings.get(var):
                os.environ[var] = value
            else:
                os.environ[var] = Prompt.ask(f"Enter {var} variable ")

    if settings is {}:
        if Confirm.ask("Would you like to save the variables ?"):
            save_to_config(vars)


def intro():
    console.clear()
    console.print("[bold frame white]\tThis is Coverse.[/bold frame white]")

def display_page(page):
    console.print(f"[bold]{page.title}[/bold]")
    console.print(page.text)
    for i, command in enumerate(page.commands.name):
        console.print(f"{i+1}. {command}")

@app.async_command()
async def play():
    intro()
    page_id = 0
    while True:
        console.clear()
        page = get_page(page_id)
        if not page:
            console.print(f"[bold red]Could not find page: {page_id}[/bold red]")
            time.sleep(1)
            if Confirm.ask(f"Would you like to continue the story by writing page {page_id} ?"):
                await create_page(id=page_id)
            break

        display_page(page)

        commands = [c.lower() for c in page.commands.name]
        command = Prompt.ask(f"[bold green]> [/bold green]")
        command_index = None
        while command_index is None:
            if command.isdigit():
                command_index = int(command) - 1
                if command_index < 0 or command_index >= len(page.commands.name):
                    command_index = None
            else:
                if command.lower() in commands:
                    command_index = commands.index(command)
            if command_index is None:
                console.print("[bold red]Invalid command. Please try again.[/bold red]")
                command = Prompt.ask(f"[bold green]> [/bold green]")

        page_id = int(page.commands.page[command_index].split(':')[1])
        console.print(page.commands.text[command_index])
        time.sleep(0.3)
        console.print(f"[bold blue]Turning to page {page_id}[/bold blue]")
        time.sleep(1)

if __name__ == "__main__":
    check_envs()
    session = create_authenticated_session()
    app()
