from pydantic import BaseModel, TypeAdapter
from typing import Literal, List, Optional, Annotated

class Command(BaseModel):
    name: str
    text: str
    page: int

class CreatePage(BaseModel):
    id: int
    title: str
    text: str
    limit: int
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

CreateCommands = TypeAdapter(List[Command])
