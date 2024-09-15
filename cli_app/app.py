from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.text import Text
from typing import List
from rich import print_json
import random
import time
import os
import yaml
import requests
from async_typer import AsyncTyper
import readline

from utils.db import create_authenticated_session, get_page
from create import app as create_app
from play import play

CONFIG_FILE_LOCATION = ".config"

if not os.path.exists(CONFIG_FILE_LOCATION):
    open(CONFIG_FILE_LOCATION, 'a+').close()

err_console = Console(stderr=True)
console = Console()

app = AsyncTyper()
app.add_typer(create_app, name="create")

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

@app.async_command('play')
async def main_play():
    await play()

if __name__ == "__main__":
    check_envs()
    session = create_authenticated_session()
    try:
        app()
    except Exception as e:
        print(e)
