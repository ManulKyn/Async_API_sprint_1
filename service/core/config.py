import os
from logging import config as logging_config

from pydantic import BaseSettings
from dotenv import load_dotenv
from core.logger import LOGGING

# Применяем настройки логирования
logging_config.dictConfig(LOGGING)
load_dotenv()


class Settings(BaseSettings):
    # Название проекта. Используется в Swagger-документации
    PROJECT_NAME: str = os.getenv('PROJECT_NAME', 'movies')

    # Настройки Redis
    REDIS_HOST: str = os.getenv('REDIS_HOST', '127.0.0.1')
    REDIS_PORT: int = os.getenv('REDIS_PORT', 6379)

    # Настройки Elasticsearch
    ELASTIC_HOST: str = os.getenv('ELASTIC_HOST', '127.0.0.1')
    ELASTIC_PORT: int = os.getenv('ELASTIC_PORT', 9200)

    # Корень проекта
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Ответ при отсутвии данных
    NO_FILM_FND: str = os.getenv('NO_FILM_FND', 'film not found')
    NO_GENRE_FND: str = os.getenv('NO_GENRE_FND', 'genre not found')
    NO_GENRES_FND: str = os.getenv('NO_GENRES_FND', 'no genres found')
    NO_PERSON_FND: str = os.getenv('NO_PERSON_FND', 'person not found')

    # Время жизни кэша
    CACHE_EXPIRE: int = os.getenv('CACHE_EXPIRE', 360)

    class Config:
        env_file = '.env'


settings = Settings()
