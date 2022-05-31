from http import HTTPStatus
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from services.genres import GenreService, get_genre_service

from .base import SearchRequest
from core.config import settings
from fastapi_cache.decorator import cache

router = APIRouter()


class Genre(BaseModel):
    uuid: UUID
    name: str


@router.get('/{genre_id}', response_model=Genre)
@cache(expire=settings.CACHE_EXPIRE)
async def genre_details(genre_id: str, genre_service: GenreService = Depends(get_genre_service)) -> Genre:
    genre = await genre_service.get(genre_id)
    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=settings.NO_GENRE_FND)

    return Genre(uuid=genre.id, name=genre.name)


@router.get('/')
@cache(expire=settings.CACHE_EXPIRE)
async def genre_main(
        sort: Optional[str] = None,
        genre_service: GenreService = Depends(get_genre_service)
) -> List[Genre]:
    genres = await genre_service.get_all(sort=sort)
    if not genres:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=settings.NO_GENRES_FND)
    return [Genre(uuid=x.id, name=x.name) for x in genres]


@router.post('/search/')
@cache(expire=settings.CACHE_EXPIRE)
async def genre_search(
        search: SearchRequest,
        genre_service: GenreService = Depends(get_genre_service)
) -> List[Genre]:
    genres = await genre_service.search(body=search.dict(by_alias=True))
    if not genres:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=settings.NO_GENRES_FND)
    return [Genre(uuid=x.id, name=x.name) for x in genres]
