from http import HTTPStatus
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from services.persons import PersonService, get_person_service

from .base import SearchRequest

router = APIRouter()


class Person(BaseModel):
    uuid: UUID
    full_name: str


@router.post('/search/')
async def person_search(
        search: SearchRequest,
        person_service: PersonService = Depends(get_person_service)) -> List[Person]:
    persons_all_fields_search = await person_service.search(body=search.dict(by_alias=True))
    persons = [Person(uuid=x.id, full_name=x.full_name) for x in persons_all_fields_search]
    return persons


@router.get('/{person_id}', response_model=Person)
async def person_details(person_id: str, person_service: PersonService = Depends(get_person_service)) -> Person:
    person = await person_service.get(person_id)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='person not found')

    return Person(uuid=person.id, full_name=person.full_name)


@router.get('/')
async def person_main(
        sort: str,
        person_service: PersonService = Depends(get_person_service)
) -> List[Person]:
    persons_all_fields = await person_service.get_all(sort=sort)
    persons = [Person(uuid=x.id, title=x.title, imdb_rating=x.imdb_rating) for x in persons_all_fields]
    return persons
