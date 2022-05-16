from typing import Optional, List, Tuple, Dict, Coroutine, Any

from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from db.elastic import get_elastic
from db.redis import get_redis
from models.person import Person


class PersonService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def _get_person_from_elastic(self, person_id: str) -> Optional[Person]:
        doc = await self.elastic.get('persons', person_id)
        return Person(**doc['_source'])

    async def _get_person_full(self, person_id: str) -> Dict[str, List[str]]:
        ids_films_writer = await self.role_films(person_id=person_id, role='writers')
        ids_films_director = await self.role_films(person_id=person_id, role='directors')
        ids_films_actor = await self.role_films(person_id=person_id, role='actors')

        role_list = {
            'writer': ids_films_writer,
            'director': ids_films_director,
            'actor': ids_films_actor
        }
        return role_list

    async def role_films(self, person_id: str, role: str) -> list:
        body = {
            'query': {
                'bool': {
                    'filter': {
                        'nested': {
                            'path': role,
                            'query': {
                                'bool': {
                                    'filter': {
                                        'term': {role + '.id': person_id}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        ids_films = await self.search_role_ids(body=body)
        return ids_films

    async def search_role_ids(self, body: Dict):
        doc = await self.elastic.search(index='movies', body=body, size=10000)
        ids_films = [x['_source']['id'] for x in doc['hits']['hits']]
        return ids_films

    async def person_search(self, query: str, page_size: int, page_number: int):
        body = {
            'size': page_size,
            'from': (page_number - 1) * page_size,
            'query': {
                'simple_query_string': {
                    "query": query,
                    "fields": ["full_name"],
                    "default_operator": "or"
                }
            }
        }
        doc = await self.elastic.search(index='persons', body=body, size=10000)
        persons = [Person(**x['_source']) for x in doc['hits']['hits']]
        return persons


def get_person_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(redis, elastic)
