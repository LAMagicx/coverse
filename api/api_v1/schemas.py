# api_v1/schemas.py
from pydantic import BaseModel
from typing import List, Optional

class CreateCommand(BaseModel):
    name: str
    text: str
    page: int

class CreatePage(BaseModel):
    id: int
    title: str
    text: str
    commands: List[CreateCommand]

class Commands(BaseModel):
    name: List[str]
    text: List[str]
    page: List[str]

class Page(BaseModel):
    id: str
    title: str
    text: str
    commands: Commands
