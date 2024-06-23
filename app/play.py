import requests
import time
import readline
from typing import Literal, List
from pydantic import BaseModel
from rich.console import Console
from rich.prompt import Prompt

class Commands(BaseModel):
    name: List[str]
    text: List[str]
    page: List[str]

class Page(BaseModel):
    id: str
    title: str
    text: str
    commands: Commands

API_URL = "http://localhost/api"
USERNAME = 'magic'
PASSWORD = 'heard-linux-rain'

class LoginError(Exception):
    def __init__(self, status_code):
        self.status_code = status_code
        super().__init__(f"Login failed with status code: {status_code}")


def fetch_access_token(username: str, password: str) -> str:
    LOGIN_URL = API_URL + "/v1/auth/login"
    response = requests.post(LOGIN_URL,
                             headers={"Accept": "application/json", "Content-Type": "application/json"},
                             json={"username": username, "password": password})
    if response.status_code == 200:
        return response.json()['token']
    else:
        raise LoginError(response.status_code)

def create_authenticated_session() -> requests.Session:
    global session 
    token = fetch_access_token(USERNAME, PASSWORD)
    session = requests.Session()
    session.headers.update({"Authorization": f"Bearer {token}",
                            "Accept": "application/json",
                            "Content-Type": "application/json"})
    return session

def make_request(method: Literal["GET", "POST"], endpoint: str, data: dict={}, params: dict={}) -> dict:
    if method == "GET":
        response = session.get(API_URL + endpoint, data=data, params=params)
    elif method == "POST":
        response = session.post(API_URL + endpoint, data=data, params=params)
    else:
        raise Exception(f"Request {type} not implemented")

    return response

def get_page(page_id):
    for _ in range(3):
        time.sleep(0.1)
        res = make_request("GET", f"/v1/pages/{page_id}")
        if res.status_code == 200:
            return Page.validate(res.json())
    return None


def main_loop():
    page_id = 0
    while True:
        page = get_page(page_id)
        if not page:
            console.print(f"[bold red]Could not find page: {page_id}[/bold red]")
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
        console.print(f"[bold blue]Turning to page {page_id}[/bold blue]")




if __name__ == "__main__":
    session = create_authenticated_session()
    console = Console()
    create_page()
