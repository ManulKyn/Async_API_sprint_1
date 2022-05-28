from abc import ABC, abstractmethod
from typing import Type, Union

from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_scan
from models.film import Film
from models.genre import Genre
from models.person import Person


class Service(ABC):
    @property
    @abstractmethod
    def index(self) -> str:
        pass

    @property
    @abstractmethod
    def model(self) -> Type[Union[Film, Genre, Person]]:
        pass

    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def search(self, body):
        resp = await self.elastic.search(
            index=self.index,
            body=body
        )
        return [self.model(**doc['_source']) for doc in resp['hits']['hits']]

    async def get_all(self, **kwargs):
        q = {"query": {"match_all": {}}}

        if param := kwargs.get('sort'):
            order_value = 'asc'
            if param.startswith('-'):
                param = param[1:]
                order_value = 'desc'
            q['sort'] = [{param: {'order': order_value}}]

        response_list = []

        async for doc in async_scan(
                client=self.elastic,
                size=q.get('size', 10000),
                index=self.index,
                query=q,
                preserve_order=True
        ):
            response_list.append(self.model(**doc['_source']))

        return response_list

    async def get(self, id_: str):
        response = await self.elastic.get(index=self.index, id=id_)
        return self.model(**response['_source'])
