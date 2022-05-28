from typing import Type

from aioredis import Redis
from db.elastic import get_elastic
from db.redis import get_redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from models.genre import Genre

from .base import Service


class GenreService(Service):
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        super(GenreService, self).__init__(redis=redis, elastic=elastic)

    @property
    def index(self) -> str:
        return 'genres'

    @property
    def model(self) -> Type[Genre]:
        return Genre


def get_genre_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    return GenreService(redis, elastic)
