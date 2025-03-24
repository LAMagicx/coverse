import os
from typing import Optional, List
from pydantic import BaseModel

from flask import Flask, render_template, send_file, request, url_for, redirect, session
from flask_session import Session
from requests import status_codes

import hashlib

from db import SurrealDB, SurrealTable

SurrealDB.connect("http://localhost:8000",
                  "root", # os.environ.get("SURREAL_USERNAME", "root"),
                  "notroot", # os.environ.get("SURREAL_PASSWORD", "root"),
                  "python",
                  "database_test")

class Command(BaseModel):
    name: str
    text: str
    page: int | str
    required: List[Optional[int | str]] = []

class Page(SurrealTable):
    title: str
    text: str
    limit: int
    commands: List[Optional[Command]] = []
                  

app = Flask(__name__)

app.config["SESSION_TYPE"] = "cachelib"
Session(app)


@app.errorhandler(404)
def page_not_found(e):
    print(f"404: {e}")
    return render_template("404.html"), 404

@app.before_request
def check_token():
    print("here")
    print(session)
    if "visits" not in session:
        session["visits"] = {}

    if "user_id" not in session.keys():
        ua = request.headers.get("User-Agent")
        ip = request.access_route[-1]
        uid = f"{ip}_{hashlib.sha1(ua.encode('utf-8')).hexdigest()[:8]}"
        print(f"New user: {uid}")
        session["user_id"] = uid


@app.route("/")
def home():
    return render_template("home.html")

@app.route("/page/<int:page_id>", methods=["GET"])
def show_page(page_id: int):
    user_id = session['user_id']
    if user_id not in session["visits"]:
        session["visits"][user_id] = [] 

    session["visits"][user_id].append(page_id)

    page = Page.select(page_id)
    if page is None:
        return render_template('not_found.html')

    return render_template('page.html', page=page)


@app.route("/create/<int:page_id>", methods=["GET", "POST"])
def create_page(page_id: int):


if __name__ == "__main__":

    app.run(host="0.0.0.0", port=8085)
