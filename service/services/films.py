from typing import Dict, List, Optional

from aioredis import Redis
from db.elastic import get_elastic
from db.redis import get_redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from models.film import Film


class FilmService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def search_films(self, body: Dict):
        doc = await self.elastic.search(index='movies', body=body)
        list_films = [Film(**x['_source']) for x in doc['hits']['hits']]
        return list_films

    async def get_film_search(self, query: dict, page_size: int, page_number: int, sort: dict) -> List[Film]:
        body = {
            'size': page_size,
            'from': page_number,
            'query': query,
            'sort': sort
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

    async def _get_film_from_elastic(self, film_id: str) -> Optional[Film]:
        doc = await self.elastic.get('movies', film_id)
        return Film(**doc['_source'])

    async def get_by_id(self, film_id: str) -> Optional[Film]:
        film = await self._get_film_from_elastic(film_id)
        if not film:
            return None
        return film


def get_film_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(redis, elastic)
