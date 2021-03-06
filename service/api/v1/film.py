from http import HTTPStatus
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from services.films import FilmService, get_film_service

from .base import SearchRequest
from core.config import settings
from fastapi_cache.decorator import cache

router = APIRouter()


class FilmMain(BaseModel):
    uuid: Optional[UUID]
    title: Optional[str]
    imdb_rating: Optional[float]


class FilmDetail(FilmMain):
    description: Optional[str]
    genre: Optional[List[str]]
    actors: Optional[List[dict]]
    writers: Optional[List[dict]]
    director: Optional[str]


@router.post('/search/')
@cache(expire=settings.CACHE_EXPIRE)
async def film_search(
        search: SearchRequest,
        film_service: FilmService = Depends(get_film_service)) -> List[FilmMain]:
    films_all_fields_search = await film_service.search(body=search.dict(by_alias=True))
    return [FilmMain(uuid=x.id, title=x.title, imdb_rating=x.imdb_rating) for x in films_all_fields_search]


@router.get('/{film_id}', response_model=FilmDetail)
@cache(expire=settings.CACHE_EXPIRE)
async def film_details(film_id: str, film_service: FilmService = Depends(get_film_service)) -> FilmDetail:
    film = await film_service.get(film_id)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=settings.NO_FILM_FND)

    return FilmDetail(uuid=film.id, title=film.title, imdb_rating=film.imdb_rating, description=film.description,
                      genre=film.genre, actors=film.actors, writers=film.writers, director=film.director)


@router.get('/')
@cache(expire=settings.CACHE_EXPIRE)
async def film_main(
        sort: Optional[str] = "-imdb_rating",
        film_service: FilmService = Depends(get_film_service)
) -> List[FilmMain]:
    films_all_fields = await film_service.get_all(sort=sort)
    return [FilmMain(uuid=x.id, title=x.title, imdb_rating=x.imdb_rating) for x in films_all_fields]
