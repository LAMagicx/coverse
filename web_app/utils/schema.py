from pydantic import BaseModel, TypeAdapter
from typing import List, Optional


class Command(BaseModel):
    name: str
    text: str
    page: str | int
    required: Optional[List[int | str]] = []


class CreatePage(BaseModel):
    id: int | str
    title: str
    text: str
    limit: int | str
    commands: Optional[List[Command]] = []


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


CreateCommands = TypeAdapter(List[Command])
