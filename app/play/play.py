from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.text import Text
from async_typer import AsyncTyper
import time
import typer
import json
import readline
import random

from functools import wraps
import anyio

from create import create_page
from utils.db import get_page

err_console = Console(stderr=True)
console = Console()

def pause(delay: float, x: int):
    if x % 5 == 0: 
        x += 1
        time.sleep(abs(random.gauss(delay * 10, 0.02)))
    else:
        time.sleep(abs(random.gauss(delay, 0.02)))
    return x


def slow_print(msg: str, style: str="", delay: float=0.01):
    space_count = 0
    msg += " "
    for i in range(len(msg)):
        if msg[i] == ' ':
            space_count += 1
        if style:
            console.print(f"[{style}]{msg[i]}[/{style}]", end='')
        else:
            console.print(f"{msg[i]}", end='')
        space_count = pause(delay, space_count)
    print("")

def intro():
    console.clear()
    console.print("[bold frame white]\tThis is Coverse.[/bold frame white]")

def display_page(page):
    time.sleep(0.5)
    slow_print(page.title, style="bold", delay=0.06)
    slow_print(page.text)
    for i, command in enumerate(page.commands.name):
        pause(0.05, i)
        slow_print(f"{i+1}. {command}")


def async_callback(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        @app.callback(invoke_without_command=True)
        async def coro_wrapper():
            return await func(*args, **kwargs)

        return anyio.run(coro_wrapper)

    return wrapper

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
        command = Prompt.ask(f"[bold green blink]> [/bold green blink]")
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
