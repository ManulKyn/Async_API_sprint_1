import uuid
from typing import List, Optional

from pydantic import BaseModel, Field


class NestedNames(BaseModel):
    id: uuid.UUID
    name: str


class FilmWorkTableSchema(BaseModel):
    id: uuid.UUID
    imdb_rating: Optional[str]
    title: str
    description: Optional[str]


class GenreTableSchema(BaseModel):
    id: uuid.UUID
    genre: Optional[List[str]]


class PersonTableSchema(BaseModel):
    id: uuid.UUID
    director: Optional[str]
    actors_names: Optional[List[Optional[str]]] = Field(default_factory=list)
    writers_names: Optional[List[Optional[str]]] = Field(default_factory=list)
    actors: Optional[List[Optional[NestedNames]]] = Field(default_factory=list)
    writers: Optional[List[Optional[NestedNames]]] = Field(default_factory=list)
