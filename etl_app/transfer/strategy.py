import datetime
import logging
import os
from abc import ABC, abstractmethod
from typing import Generator, Iterator, List, Type, Union

from psycopg2 import OperationalError, extras
from psycopg2._psycopg import cursor as psy_cursor

from .elastic import EsManagement
from .utils import backoff, postgres_connection
from .validators import (FilmWorkTableSchema, GenreTableSchema,
                         PersonTableSchema)


class ContentTableStrategyFabric(ABC):
    """Интерфейс стратегии извлечения данных"""

    schema = 'content'
    table_name: str = None
    es_client = EsManagement()

    @property
    @abstractmethod
    def validator(self) -> Type[Union[FilmWorkTableSchema, PersonTableSchema, GenreTableSchema]]:
        pass

    @backoff(timeout_restriction=180, time_factor=2, exception=OperationalError)
    def extract(
            self,
            reference_date_start: datetime.datetime,
            reference_date_end: datetime.datetime,
            query_limit: int,
            offset: int
    ) -> List[dict]:
        """Основной метод, отвечающий за извлечение данных"""
        with postgres_connection(
                dbname=os.environ.get('DB_NAME'),
                user=os.environ.get('DB_USER'),
                password=os.environ.get('DB_PASSWORD'),
                host=os.environ.get('DB_HOST', '127.0.0.1'),
                port=os.environ.get('DB_PORT', 5432),
                cursor_factory=extras.RealDictCursor
        ) as conn, conn.cursor(cursor_factory=extras.RealDictCursor) as cursor:
            self.strategy_extra_query(
                cursor=cursor,
                reference_date_start=reference_date_start,
                reference_date_end=reference_date_end,
                query_limit=query_limit,
                offset=offset
            )
            result = cursor.fetchall()

        return result

    def transform(self, queryset: List[dict]) -> Generator:
        """
        Логика трансформации результатов запроса обновленных данных под схему elasticsearch при обновлении результатов
        """

        return (self.validator(**row).dict(by_alias=True) for row in queryset)

    @abstractmethod
    def strategy_extra_query(
            self,
            cursor: psy_cursor,
            reference_date_start: datetime.datetime,
            reference_date_end: datetime.datetime,
            query_limit: int,
            offset: int
    ) -> str:
        """Логика извлечения данных для конкретной таблицы"""
        pass

    @backoff(timeout_restriction=180, time_factor=2)
    def load(self, qs: Iterator[dict]):
        self.es_client.upsert(query_set=qs)


class FilmWorkTableStrategyFabric(ContentTableStrategyFabric):
    table_name = 'film_work'

    @property
    def validator(self) -> Type[Union[FilmWorkTableSchema, PersonTableSchema, GenreTableSchema]]:
        return FilmWorkTableSchema

    def strategy_extra_query(
            self,
            cursor: psy_cursor,
            reference_date_start: datetime.datetime,
            reference_date_end: datetime.datetime,
            query_limit: int,
            offset: int
    ):
        sql = f"""
                SELECT
                    id,
                    rating as imdb_rating,
                    title,
                    description
                FROM {self.schema}.{self.table_name}
                WHERE updated_at BETWEEN '{reference_date_start}' AND '{reference_date_end}'
                offset({offset})
                limit ({query_limit});
                """
        cursor.execute(sql)


class GenreTableStrategyFabric(ContentTableStrategyFabric):
    table_name = 'genre'

    @property
    def validator(self) -> Type[Union[FilmWorkTableSchema, PersonTableSchema, GenreTableSchema]]:
        return GenreTableSchema

    def strategy_extra_query(
            self,
            cursor: psy_cursor,
            reference_date_start,
            reference_date_end,
            query_limit: int,
            offset: int
    ):
        sql = f"""
                SELECT pfw.film_work_id id, array_agg(source.name) as genre
                FROM {self.schema}.{self.table_name} source
                JOIN {self.schema}.genre_film_work pfw ON pfw.genre_id = source.id
                WHERE source.updated_at BETWEEN '{reference_date_start}' AND '{reference_date_end}'
                GROUP BY pfw.film_work_id
                offset ({offset})
                limit ({query_limit});
                """
        cursor.execute(sql)


class PersonTableStrategyFabric(ContentTableStrategyFabric):
    table_name = 'person'

    @property
    def validator(self) -> Type[Union[FilmWorkTableSchema, PersonTableSchema, GenreTableSchema]]:
        return PersonTableSchema

    def strategy_extra_query(
            self,
            cursor: psy_cursor,
            reference_date_start: datetime.datetime,
            reference_date_end: datetime.datetime,
            query_limit: int,
            offset: int
    ):
        sql = f"""
                SELECT
                    source.film_work_id id,
                    COALESCE (
                        json_agg(
                            DISTINCT jsonb_build_object(
                                'person_role', source.role,
                                'person_id', persons.id,
                                'person_name', persons.full_name
                            )
                        ) FILTER (WHERE persons.id is not null),
                        '[]'
                    ) as persons
                FROM content.person_film_work source
                JOIN (
                    SELECT distinct pfw.film_work_id
                    FROM content.person_film_work pfw
                    JOIN  (
                        SELECT id FROM content.person
                        WHERE updated_at BETWEEN '{reference_date_start}' AND '{reference_date_end}'
                    ) updated on updated.id = pfw.person_id
                ) sub ON sub.film_work_id = source.film_work_id
                JOIN content.person persons ON persons.id = source.person_id
                GROUP BY source.film_work_id
                offset ({offset})
                limit ({query_limit});
                """
        cursor.execute(sql)

    def transform(self, queryset: List[dict]):
        for row in queryset:
            line = self.validator(id=row['id']).dict()
            for person in row['persons']:
                if person['person_role'] == 'director':
                    logging.warning(person)
                    line['director'] = person['person_name']
                else:
                    line[f'{person["person_role"]}s'].append(
                        {'name': person["person_name"], 'id': person["person_id"]}
                    )
                    line[f'{person["person_role"]}s_names'].append(person["person_name"])

            validated = self.validator(**line).dict()
            logging.warning(f"{row},\n\n{validated}\n\n")
            yield validated
