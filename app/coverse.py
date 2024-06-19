import requests
import time
from typing import Literal, List
from pydantic import BaseModel

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
PASSWORD = ''

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
        raise LoginError

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


if __name__ == "__main__":
    session = create_authenticated_session()
    
    page_id = 0
    while True:
        for _ in range(3):
            time.sleep(0.1)
            res = make_request("GET", f"/v1/pages/{page_id}")
            if res.status_code == 200:
                page = Page.validate(res.json())
                break
        else:
            print(f"Could not find page: {page_id}")
            break

        print(page.id)
        print(page.title)
        print(page.text)
        print(page.commands.name)
        command = input("> ")
        while command not in page.commands.name:
            print("not a known command. please try again")
            command = input("> ")
        index = page.commands.name.index(command)
        page_id = int(page.commands.page[index].split(':')[1])
        print(page.commands.text[index])
        print(f"turing to page {page_id}")


