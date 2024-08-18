# api_v1/schemas.py
from pydantic import BaseModel, TypeAdapter
from typing import List, Optional

class AuthDetails(BaseModel):
    username: str
    password: str

class Command(BaseModel):
    name: str
    text: str
    page: str | int
    required: List[int | str] | None = []

class Page(BaseModel):
    id: int | str
    title: str
    text: str
    limit: int | str
    commands: List[Optional[Command]] | None = []

Pages = TypeAdapter(List[Page])

class FetchCommands(BaseModel):
    name: List[str]
    text: List[str]
    page: List[str]
    requires: Optional[List[str]] | None = []

class FetchPage(BaseModel):
    id: str
    title: str
    text: str
    commands: FetchCommands

FetchPages = TypeAdapter(List[FetchPage])

class PageQuery(BaseModel):
    id: str
    title: str
    text: str
    score: float
    commands: dict

PageQueries = TypeAdapter(List[PageQuery])
