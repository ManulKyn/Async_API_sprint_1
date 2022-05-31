from http import HTTPStatus
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from services.persons import PersonService, get_person_service

from .base import SearchRequest
from core.config import settings
from fastapi_cache.decorator import cache

router = APIRouter()


class Person(BaseModel):
    uuid: UUID
    full_name: str


@router.post('/search/')
@cache(expire=settings.CACHE_EXPIRE)
async def person_search(
        search: SearchRequest,
        person_service: PersonService = Depends(get_person_service)) -> List[Person]:
    persons_all_fields_search = await person_service.search(body=search.dict(by_alias=True))
    return [Person(uuid=x.id, full_name=x.full_name) for x in persons_all_fields_search]


@router.get('/{person_id}', response_model=Person)
@cache(expire=settings.CACHE_EXPIRE)
async def person_details(person_id: str, person_service: PersonService = Depends(get_person_service)) -> Person:
    person = await person_service.get(person_id)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=settings.NO_PERSON_FND)
    return Person(uuid=person.id, full_name=person.full_name)


@router.get('/')
@cache(expire=settings.CACHE_EXPIRE)
async def person_main(
        sort: Optional[str] = None,
        person_service: PersonService = Depends(get_person_service)
) -> List[Person]:
    persons_all_fields = await person_service.get_all(sort=sort)
    return [Person(uuid=x.id, title=x.title, imdb_rating=x.imdb_rating) for x in persons_all_fields]
