import abc
import time
import json
from typing import List, Tuple, Generator, Any, Optional
from dataclasses import dataclass

from db import PostgresDatabase
from coroutine import coroutine
from backoff import backoff


class BaseStorage:
    @abc.abstractmethod
    def save_state(self, state: dict) -> None:
        """Сохранить состояние в постоянное хранилище"""
        pass

    @abc.abstractmethod
    def retrieve_state(self) -> dict:
        """Загрузить состояние локально из постоянного хранилища"""
        pass


class JsonFileStorage(BaseStorage):
    def __init__(self, file_path: Optional[str] = None):
        self.file_path = file_path

    def save_state(self, state: dict) -> None:
        try:
            with open(self.file_path, 'w') as f:
                f.write(json.dumps(state))
        except FileNotFoundError:
            return {}

    def retrieve_state(self) -> dict:
        try:
            with open(self.file_path, 'r') as f:
                body = f.read()
                return json.loads(body) if body else None
        except FileNotFoundError:
            return {}


class State:
    def __init__(self, storage: BaseStorage):
        self.storage = storage
        self.state = self.retrieve_state()

    @backoff()
    def retrieve_state(self) -> dict:
        data = self.storage.retrieve_state()
        if not data:
            return {}
        return data

    @backoff()
    def set_state(self, key: str, value: Any) -> None:
        """Установить состояние для определённого ключа"""
        self.state[key] = value
        self.storage.save_state(self.state)

    @backoff()
    def get_state(self, key: str) -> Any:
        """Получить состояние по определённому ключу"""
        return self.state.get(key) if self.state else None


@dataclass
class Lookup:
    db: PostgresDatabase
    storage: JsonFileStorage

    @property
    def state(self):
        return State(
            self.storage
        )

    def produce(self, target: Generator):
        pass

    def get_updated_rows(
        self,
        table: str,
        timestamp_column: str = 'updated_at',
        columns: Tuple[str] = None,
        flat: bool = False,
    ) -> Generator:
        columns = columns or []

        def inner(target: Generator):
            batch_num = 0
            batch_size = 100

            while True:
                state = self.state

                last_updated_at = None
                if last_updated_at__str := state.get_state('last_updated_at'):
                    last_updated_at = dateutil.parser.parse(
                        last_updated_at__str
                    )
                last_id = state.get_state('last_id')

                select_columns = ', '.join(['id', timestamp_column, *columns])
                updated_rows: List[dict] = self.db.query(
                    f'''
                    SELECT {select_columns}
                    FROM {table}
                    '''
                    + f'''
                    WHERE {timestamp_column} = %(last_updated_at)s
                    and id > %(last_id)s::uuid
                    or {timestamp_column} > %(last_updated_at)s
                    ''' * bool(last_updated_at)
                    + f'''
                    ORDER BY {timestamp_column}, id
                    LIMIT %(batch_size)s
                    ''',
                    {
                        'last_updated_at': last_updated_at,
                        'last_id': last_id,
                        'batch_size': batch_size,
                    }
                )
                time.sleep(0.5)

                if not updated_rows:
                    break

                last = updated_rows[-1]
                results: List[dict] = updated_rows
                if columns:
                    results = [{c: row[c] for c in columns} for row in results]
                if len(columns) == 1 and flat:
                    target.send(results)
                state.set_state('last_updated_at', str(last[timestamp_column]))
                state.set_state('last_id', last[id])
                batch_num += 1
        return inner


@dataclass
class PersonLookup(Lookup):
    def produce(self, target: Generator):
        get_update_persons = self.get_updated_rows(
            'content.person',
            'updated_at'
        )
        get_update_persons(
            self._get_person_films(
                target
            )
        )

    @coroutine
    def _get_person_films(self, target: Generator):
        updated_persons: List[dict]

        while updated_persons := (yield):
            person_ids = [person['id'] for person in updated_persons]
            person_films: List[dict] = self.db.query(
                '''
                SELECT
                    pfw.film_work_id as id
                FROM content.person_film_work pfw
                WHERE pfw.person_id = ANY (%(person_ids)s::uuid[])
                ''',
                {
                    'person_ids': person_ids
                }
            )
            film_ids: List[str] = [film['id'] for film in person_films]
            time.sleep(0.5)
            target.send(film_ids)


@dataclass
class PersonFilmLookup(Lookup):
    def produce(self, target: Generator):
        get_created_film_roles = self.get_updated_rows(
            'content.person_film_work',
            'created_at',
            columns=('film_work_id',),
            flat=True
        )
        get_created_film_roles(target)


@dataclass
class GenreLookup(Lookup):
    def produce(self, target: Generator):
        get_update_genres = self.get_updated_rows(
            'content.genre',
            'updated_at'
        )
        get_update_genres(
            self._get_genre_films(
                target
            )
        )

    @coroutine
    def _get_genre_films(self, target: Generator):
        updated_genres: List[dict]

        while updated_genres := (yield):
            genre_ids = [person['id'] for person in updated_genres]
            genre_films: List[dict] = self.db.query(
                '''
                SELECT
                    gfw.film_work_id as id
                FROM content.genre_film_work gfw
                WHERE gfw.genre_id = ANY (%(person_ids)s::uuid[])
                ''',
                {
                    'genre_ids': genre_ids
                }
            )
            film_ids: List[str] = [film['id'] for film in genre_films]
            time.sleep(0.5)
            target.send(film_ids)


@dataclass
class GenreFilmLookup(Lookup):
    def produce(self, target: Generator):
        get_created_genres = self.get_updated_rows(
            'content.genre_film_work',
            'created_at',
            columns=('film_work_id',),
            flat=True
        )
        get_created_genres(target)
