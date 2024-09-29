# api_v1/schemas.py
from pydantic import BaseModel, TypeAdapter, Field
from typing import List, Optional


class AuthDetails(BaseModel):
    username: str = Field(..., max_length=16)
    password: str = Field(..., max_length=32)


class Command(BaseModel):
    name: str = Field(..., max_length=64)
    text: str = Field(..., max_length=64)
    page: int = Field(ge=0, le=1024)
    required: List[Optional[int]] = []


class Page(BaseModel):
    id: int = Field(ge=0, le=1024)
    title: str = Field(..., max_length=64)
    text: str = Field(..., max_length=258)
    limit: int = Field(ge=1, le=8)
    commands: List[Optional[Command]] = []


Pages = TypeAdapter(List[Page])


class FetchCommands(BaseModel):
    name: List[str]
    text: List[str]
    page: List[str]
    required: List[List[Optional[str]]] = []


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


class ParentCommand(BaseModel):
    name: str
    text: str


class ParentPage(BaseModel):
    command: ParentCommand
    id: str
    text: str
    title: str


ParentPages = TypeAdapter(List[ParentPage])
