from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel

from .base import BaseOrjsonModel


class Film(BaseModel, BaseOrjsonModel.Config):
    id: Optional[UUID]
    title: Optional[str]
    description: Optional[str]
    imdb_rating: Optional[float]
    genre: Optional[List[str]]
    director: Optional[str]
    writers: Optional[List[dict]]
    actors: Optional[List[dict]]
    writers_names: Optional[List[str]]
    directors_names: Optional[List[str]]
    actors_names: Optional[List[str]]
