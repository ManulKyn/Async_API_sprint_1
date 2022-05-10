from functools import lru_cache
from typing import Optional, List, Dict

from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from db.elastic import get_elastic
from db.redis import get_redis
from models.film import Film

FILM_CACHE_EXPIRE_IN_SECONDS = 300


class FilmService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def search_films(self, body: Dict):
        doc = await self.elastic.search(index='movies', body=body)
        list_films = [Film(**x['_source']) for x in doc['hits']['hits']]
        return list_films

    async def get_film_search(self, query: str, page_size: int, page_number: int) -> List[Film]:
        body = {
            'size': page_size,
            'from': (page_number - 1) * page_size,
            'query': {
                'simple_query_string': {
                    "query": query,
                    "fields": ["title^3", "description"],
                    "default_operator": "or"
                }
            }
        }
        doc = await self.search_films(body)
        return doc

    async def get_film_pagination(self, sort: str, page_size: int, page_number: int, filter_genre: str) -> List[Film]:
        order_value = 'asc'
        if sort.startswith('-'):
            sort = sort[1:]
            order_value = 'desc'
        body = {
            'size': page_size,
            'from': (page_number - 1) * page_size,
            'sort': {
                sort: {
                    'order': order_value
                }
            }
        }
        if filter_genre:
            body['query'] = {
                'bool': {
                    'filter': {
                        'nested': {
                            'path': 'genres',
                            'query': {
                                'bool': {
                                    'filter': {
                                        'term': {'genres.id': filter_genre}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        doc = await self.search_films(body)
        return doc

    async def get_by_id(self, film_id: str) -> Optional[Film]:
        film = await self._film_from_cache(film_id)
        if not film:
            film = await self._get_film_from_elastic(film_id)
            if not film:
                return None
            await self._put_film_to_cache(film)

        return film

    async def _get_film_from_elastic(self, film_id: str) -> Optional[Film]:
        doc = await self.elastic.get('movies', film_id)
        return Film(**doc['_source'])

    async def _film_from_cache(self, film_id: str) -> Optional[Film]:
        data = await self.redis.get(film_id)
        if not data:
            return None
        film = Film.parse_raw(data)
        return film

    async def _put_film_to_cache(self, film: Film):
        await self.redis.set(str(film.id), film.json(), expire=FILM_CACHE_EXPIRE_IN_SECONDS)


@lru_cache()
def get_film_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(redis, elastic)
