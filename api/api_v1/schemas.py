# api_v1/schemas.py
from pydantic import BaseModel
from typing import List

class Command(BaseModel):
    name: str
    text: str
    page: str

class CreatePage(BaseModel):
    id: int
    title: str
    text: str
    commands: List[Command]

class Page(BaseModel):
    id: str
    title: str
    text: str

class Upload(BaseModel):
    pages: List[CreatePage]
