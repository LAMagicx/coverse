from typing import Literal
import requests
import time

from schema import Page, CreatePage

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

def get_page(page_id) -> Page | None:
    for _ in range(3):
        time.sleep(0.1)
        res = make_request("GET", f"/v1/pages/{page_id}")
        if res.status_code == 200:
            return Page.validate(res.json())
    return None
