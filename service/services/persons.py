from typing import Type

from aioredis import Redis
from db.elastic import get_elastic
from db.redis import get_redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from models.person import Person

from .base import Service


class PersonService(Service):
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        super(PersonService, self).__init__(redis=redis, elastic=elastic)

    @property
    def index(self) -> str:
        return 'persons'

    @property
    def model(self) -> Type[Person]:
        return Person


def get_person_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(redis, elastic)
