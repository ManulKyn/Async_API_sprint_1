import orjson
from uuid import UUID
from typing import List, Optional
from pydantic import BaseModel


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class Film(BaseModel):
    id: UUID
    title: str
    description: Optional[str] = ''
    imdb_rating: float = 0.0
    genre: List[str] = ['']
    genres: List[dict] = [{}]
    directors: List[dict] = [{}]
    writers: List[dict] = [{}]
    actors: List[dict] = [{}]
    writers_names: List[str] = ['']
    directors_names: List[str] = ['']
    actors_names: List[str] = ['']

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
