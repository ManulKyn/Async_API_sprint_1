import uuid
from typing import List, Optional

from pydantic import BaseModel, Field, validator


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
    description: Optional[str] = 'No description'


class GenrePostgreRow(BaseModel):
    id: uuid.UUID
    name: str
    description: Optional[str] = 'No description'

    @validator('description')
    def default_desc(cls, value):
        return value or 'No description'


class PersonPostgreRow(BaseModel):
    id: uuid.UUID
    full_name: str


class PersonTableSchema(BaseModel):
    id: uuid.UUID
    director: Optional[str]
    actors_names: Optional[List[Optional[str]]] = Field(default_factory=list)
    writers_names: Optional[List[Optional[str]]] = Field(default_factory=list)
    actors: Optional[List[Optional[NestedNames]]] = Field(default_factory=list)
    writers: Optional[List[Optional[NestedNames]]] = Field(default_factory=list)
