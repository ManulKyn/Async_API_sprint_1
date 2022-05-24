import logging

import aioredis
import uvicorn
from api.v1 import film, genre, person
from core import config
from core.logger import LOGGING
from db import elastic, redis
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from uuid import UUID

app = FastAPI(
    title=config.PROJECT_NAME,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
)

app.include_router(
    film.router,
    prefix='/api/v1/films',
    tags=['films'],
)

app.include_router(
    person.router,
    prefix='/api/v1/persons',
    tags=['persons'],
)

app.include_router(
    genre.router,
    prefix='/api/v1/genres',
    tags=['genres'],
)


@app.on_event('startup')
async def startup():
    redis.redis = await aioredis.from_url(
        f'redis://{config.REDIS_HOST}:{config.REDIS_PORT}',
        encoding="utf-8",
        decode_responses=True,
    )
    elastic.es = AsyncElasticsearch(
        hosts=[f'{config.ELASTIC_HOST}:{config.ELASTIC_PORT}']
    )


@app.on_event('shutdown')
async def shutdown():
    await redis.redis.close()
    await elastic.es.close()


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=8000,
        log_config=LOGGING,
        log_level=logging.DEBUG,
    )
