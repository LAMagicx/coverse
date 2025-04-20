import json
from pydantic import BaseModel
from typing import List, Optional
from web_app.db import SurrealTable, SurrealDB


SurrealDB.connect("http://localhost:8000",
                 "root",
                  "notroot",
                  "test",
                  "test")

class Command(BaseModel):
    name: str
    text: str
    page: int | str
    required: List[Optional[int | str]] = []

class Page(SurrealTable):
    title: str
    text: str
    limit: int
    commands: List[Command] = []


if __name__ == "__main__":
    pages = [Page.model_validate(page) for page in json.load(open("starter.json", "r"))]

    for page in pages:
        print("Creating Page:", page.id)
        page.delete()
        page.create()
