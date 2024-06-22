import requests
from typing import Literal, List, Optional, Annotated
from pydantic import BaseModel, TypeAdapter
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.text import Text
from rich import print_json
import typer 
import time
import json
import readline

err_console = Console(stderr=True)
console = Console()

class Command(BaseModel):
    name: str
    text: str
    page: int

class CreatePage(BaseModel):
    id: int
    title: str
    text: str
    commands: List[Command]

Pages = TypeAdapter(List[CreatePage])

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
        response = session.post(API_URL + endpoint, json=data, params=params)
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

def post_page(page: CreatePage):
    print(page)
    res = make_request("POST", f"/v1/pages/{page.id}", data=page.model_dump())
    if res.status_code == 201:
        print(f"[green]Page {page.id} successfully created.[/green]")
    elif res.status_code == 409:
        print(f"[red]Page {page.id} exists already.[/red]")
    else:
        print(f"[red]Page {page.id} failed to create.[/red]")


app = typer.Typer()
create_app = typer.Typer()
app.add_typer(create_app, name='create')

def intro():
    console.clear()
    console.print("[bold frame white]\tThis is Coverse.[/bold frame white]")

async def autocomplete_page(incomplete: str = "") -> List[int]:
    """ fetches the next 3 page id possible """
    res = make_request("GET", "/v1/sql/", params={"query": "select id from page;"})
    if res.status_code == 200:
        data = json.loads(res.content)[0]["result"]
        # ids = [int(p['id'].split(':')[1]) for p in data]
        max_id = int(max(data, key=lambda p: int(p['id'].split(':')[1]))['id'].split(':')[1])
        return [max_id + 1, max_id + 2, max_id + 3]
    else:
        return [0, 1, 2]

@create_app.command('page')
async def create_page(id: Annotated[int, typer.Option(help="The id of the page", autocompletion=autocomplete_page)] = -1,
         title: Annotated[str, typer.Option(help="The title of the page")] = "",
         text: Annotated[str, typer.Option(help="The text of the page")] = "",
         commands: Annotated[List[Command], typer.Option(help="Commands linked to this page, ex: {\"name\":\"command_name\", \"text\":\"command_text\", \"page\":id_of_next_page}")] = [],
         pages: Annotated[List[Page], typer.Option(help="Json of the page to create.")] = []):
    """ Attempts to create a page with the given arguments """
    if pages == []:
        # pages not set, create one page
        if id == -1:
            possible_ids = [str(i) for i in await autocomplete_page()]
            id = int(Prompt.ask("Enter the page id ", choices=possible_ids, default=possible_ids[0]))

        # print pages + commands that point to this id. limit 5 

        if title == "":
            title = Prompt.ask("Enter the page text ")

        if text == "":
            text = Prompt.ask("Enter the page text ")

        if commands == []:
            while Confirm.ask("Create Command ?"):
                name = Prompt.ask("Command name ")
                text = Prompt.ask("Command text ")
                # print possible pages to point to.
                page = int(Prompt.ask("Command page "))
                commands.append({"name": name, "text": text, "page": page})
        pages.append({
            "id": id,
            "title": title,
            "text": text,
            "commands": commands
        })

    pages = Pages.validate_python(pages)

    for page in pages:
        post_page(page)



if __name__ == "__main__":
    session = create_authenticated_session()
# app()
