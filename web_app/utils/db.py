from typing import Literal, Tuple
import datetime as dt
import requests
import os
import json
import base64


class LoginError(Exception):
    def __init__(self, status_code):
        self.status_code = status_code
        super().__init__(f"Login failed with status code: {status_code}")


class BearerAuth(requests.auth.AuthBase):
    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers["Authorization"] = f"Bearer {self.token}"
        return r


def fetch_access_token(
    api_url: str, username: str, password: str
) -> Tuple[str | None, int]:
    login_url = api_url + "/v1/auth/login"
    response = requests.post(
        login_url,
        headers={"Accept": "application/json", "Content-Type": "application/json"},
        json={"username": username, "password": password},
    )
    if response.status_code == 200:
        return response.json()["token"], 200
    else:
        # raise LoginError(response.status_code)
        return None, response.status_code


def create_authenticated_session() -> requests.Session:
    # """ deprecrated """"
    USERNAME = os.environ.get("COVERSE_USERNAME")
    PASSWORD = os.environ.get("COVERSE_PASSWORD")
    token, _ = fetch_access_token(USERNAME, PASSWORD)
    session = requests.Session()
    session.headers.update(
        {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
    )
    return session


def refresh_token(token: str, api_url: str, username: str, password: str):
    header, jwt, sig = token.split(".")
    data = json.loads(base64.urlsafe_b64decode(pad_base64(jwt)).decode("utf-8"))
    if data["exp"] <= dt.datetime.now().timestamp():
        # token expired
        new_token, _ = fetch_access_token(api_url, username, password)
        return new_token
    return token


def make_request(
    method: Literal["GET", "POST"],
    endpoint: str,
    data: dict = {},
    params: dict = {},
    token: str = "",
    API_URL=os.environ.get("COVERSE_API_URL"),
) -> dict:
    if method == "GET":
        response = requests.get(
            API_URL + endpoint, data=data, params=params, auth=BearerAuth(token)
        )
    elif method == "POST":
        response = requests.post(
            API_URL + endpoint, json=data, params=params, auth=BearerAuth(token)
        )
    else:
        raise Exception(f"Request {type} not implemented")

    return response


def pad_base64(data):
    """Makes sure base64 data is padded"""
    missing_padding = len(data) % 4
    if missing_padding != 0:
        data += "=" * (4 - missing_padding)
    return data
