from typing import Optional, List, Dict

from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from db.elastic import get_elastic
from db.redis import get_redis
from models.genre import Genre


class GenreService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def _get_genre_from_elastic(self, genre_id: str) -> Optional[Genre]:
        doc = await self.elastic.get('genres', genre_id)
        return Genre(**doc['_source'])

    async def genre_main(self):
        doc = await self.elastic.search(index='genres', size=1000)
        list_genres = [Genre(**x['_source']) for x in doc['hits']['hits']]
        return list_genres


def get_genre_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    return GenreService(redis, elastic)
