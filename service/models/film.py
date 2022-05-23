from typing import List, Optional
from uuid import UUID

import orjson
from pydantic import BaseModel


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class Film(BaseModel):
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

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
