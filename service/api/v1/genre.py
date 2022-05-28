from http import HTTPStatus
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from services.genres import GenreService, get_genre_service

from .base import SearchRequest

router = APIRouter()


class Genre(BaseModel):
    uuid: UUID
    name: str


@router.get('/{genre_id}', response_model=Genre)
async def genre_details(genre_id: str, genre_service: GenreService = Depends(get_genre_service)) -> Genre:
    genre = await genre_service.get(genre_id)
    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='genre not found')

    return Genre(uuid=genre.id, name=genre.name)


@router.get('/')
async def genre_main(
        sort: str,
        genre_service: GenreService = Depends(get_genre_service)
) -> List[Genre]:
    genres = await genre_service.get_all(sort=sort)
    if not genres:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='there are no genres')
    genres_list = [Genre(uuid=x.id, name=x.name) for x in genres]
    return genres_list


@router.post('/search/')
async def genre_search(
        search: SearchRequest,
        genre_service: GenreService = Depends(get_genre_service)
) -> List[Genre]:
    genres = await genre_service.search(body=search.dict(by_alias=True))
    if not genres:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='no genres found')
    genres_list = [Genre(uuid=x.id, name=x.name) for x in genres]
    return genres_list
