from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from uuid import UUID
from typing import List, Optional

from services.films import FilmService, get_film_service

router = APIRouter()


class FilmMain(BaseModel):
    uuid: UUID
    title: str
    imdb_rating: float


class FilmDetail(FilmMain):
    description: Optional[str] = ''
    genre: List[dict]
    actors: List[dict]
    writers: List[dict]
    directors: List[dict]


@router.get('/search/')
async def film_search(
        query: str,
        page_size: int = Query(50, alias="page[size]"),
        page_number: int = Query(1, alias="page[number]"),
        film_service: FilmService = Depends(get_film_service)) -> List[FilmMain]:
    films_all_fields_search = await film_service.get_film_search(query, page_size, page_number)
    films = [FilmMain(uuid=x.id, title=x.title, imdb_rating=x.imdb_rating) for x in films_all_fields_search]
    return films


@router.get('/<uuid:UUID>/', response_model=FilmDetail)
async def film_details(film_id: str, film_service: FilmService = Depends(get_film_service)) -> FilmDetail:
    film = await film_service.get_by_id(film_id)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='film not found')

    return FilmDetail(uuid=film.id, title=film.title, imdb_rating=film.imdb_rating, description=film.description,
                      genre=film.genres, actors=film.actors, writers=film.writers, directors=film.directors)


@router.get('/')
async def film_main(sort: str = "-imdb_rating",
                    page_size: int = Query(50, alias="page[size]"),
                    page_number: int = Query(1, alias="page[number]"),
                    filter_genre: str = Query(None, alias="filter[genre]"),
                    film_service: FilmService = Depends(get_film_service)) -> List[FilmMain]:
    films_all_fields = await film_service.get_film_pagination(sort, page_size, page_number, filter_genre)
    films = [FilmMain(uuid=x.id, title=x.title, imdb_rating=x.imdb_rating) for x in films_all_fields]
    return films