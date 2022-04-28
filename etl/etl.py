import os
import time
from typing import List, Tuple, Generator
from dataclasses import dataclass

from elasticsearch import Elasticsearch, helpers
from pydantic import BaseSettings
from dotenv import load_dotenv

from up_check import JsonFileStorage, Lookup, PersonLookup, \
    PersonFilmLookup, GenreLookup, GenreFilmLookup
from db import PostgresDatabase
from coroutine import coroutine
from backoff import backoff

load_dotenv()


class ETLConfig(BaseSettings):
    db_url: str = "postgresql://{user}:{password}@{host}:5432/{db}".format(
        user=os.environ.get('DB_USER'),
        password=os.environ.get('DB_PASSWORD'),
        host=os.environ.get('DB_HOST'),
        db=os.environ.get('DB_NAME')
    )
    elasticsearch_hosts: str = os.environ.get('ELASTICSEARCH_HOSTS')


@dataclass
class ETLProcess:
    db: PostgresDatabase
    config: ETLConfig
    lookup: Lookup

    @coroutine
    def extract(self, target: Generator):
        film_ids: List[str]
        while film_ids := (yield):
            films: List[dict] = self.db.query(
                '''
                SELECT
                    fw.id,
                    fw.title,
                    fw.description,
                    fw.rating,
                    fw.type,
                    fwp.persons,
                    fwg.genres,
                FROM content.film_work fw LEFT JOIN LATERAL (
                    SELECT
                        pfw.film_work_id,
                        array_agg(jsonb_build_object(
                        'id', p.id, 'full_name', p.full_name, 'role', pfw.role
                        )) as persons
                    FROM content.person_film_work pwf
                    JOIN content.person p ON p.id = pfw.person_id
                    WHERE pfw.film_work_id = fw.id
                    GROUP BY 1
                ) fwp ON TRUE
                LEFT JOIN LATERAL (
                    SELECT
                        gfw.film_work_id,
                        array_agg(jsonb_build_object(
                        'id', g.id, 'name', g.name, 'role', gfw.role
                        )) as genres
                FROM content.genre_film_work gfw
                JOIN content.genre g ON g.id = gfw.person_id
                WHERE gfw.film_work_id = fw.id
                GROUP BY 1
                ) fwg ON TRUE
                ''',
                {
                    'film_ids': film_ids
                }
            )
            time.sleep(0.5)
            target.send(films)

    @coroutine
    def transform(self, target: Generator):
        film_works: List[dict]
        while film_works := (yield):
            film_work_docs = []
            for film in film_works:
                film_work_doc = {
                    k: v for k, v in film.items()
                    if k in (
                        'id',
                        'rating',
                        'title',
                        'description',
                        'type',
                        'genres'
                    )
                }
                film_work_doc['genres_names'] = [
                    g['name'] for g in film['genres']
                ]
                film_work_doc.update({
                    'actors ': [],
                    'writers': [],
                    'director': None,
                    'actors_names': [],
                    'writers_names': []
                })
                for person in film['persons']:
                    if person['role'] == 'director':
                        film_work_doc['director'] = person['full_name']
                    if person['role'] == 'actor':
                        film_work_doc['actors_names'].append(
                            person['full_name']
                        )
                        film_work_doc['actors'].append(
                            {'id': person['id'], 'name': person['full_name']}
                        )
                    if person['role'] == 'writer':
                        film_work_doc['writers_names'].append(
                            person['full_name']
                        )
                        film_work_doc['writers'].append(
                            {'id': person['id'], 'name': person['full_name']}
                        )
                film_work_docs.append(film_work_doc)
                target.send(film_work_docs)

    @backoff()
    def _bulk_update_elastic(self, docs: List[dict]) -> Tuple[int, list]:
        elastic_settings = dict(
            hosts=self.config.elasticsearch_hosts,
        )

        def generate_doc(docs):
            for doc in docs:
                yield {
                    '_index': 'movies',
                    '_id': doc['id'],
                    '_source': doc
                }
        with Elasticsearch(**elastic_settings) as es:
            return helpers.bulk(es, generate_doc(docs))

    @coroutine
    def load_to_elastic(self):
        docs: List[dict]

        while docs := (yield):
            docs_updated, _ = self._bulk_update_elastic(docs)
            time.sleep(0.5)

    def run(self):
        self.lookup.produce(
            self.extract(
                self.transform(
                    self.load_to_elastic()
                )
            )
        )


@dataclass
class ETLManager:
    processes: List[ETLProcess]

    def loop_processes(self):
        while True:
            for process in self.processes:
                process.run()
            time.sleep(3)


if __name__ == '__main__':
    config = ETLConfig()
    db = PostgresDatabase(url=config.db_url)
    storage = JsonFileStorage('./storage.txt')
    lookup_params = {'db': db, 'storage': storage}

    processes = [
        ETLProcess(
            db=db,
            config=config,
            lookup=PersonLookup(**lookup_params)
        ),
        ETLProcess(
            db=db,
            config=config,
            lookup=PersonFilmLookup(**lookup_params)
        ),
        ETLProcess(
            db=db,
            config=config,
            lookup=GenreLookup(**lookup_params)
        ),
        ETLProcess(
            db=db,
            config=config,
            lookup=GenreFilmLookup(**lookup_params)
        ),
    ]

    manager = ETLManager(processes=processes)
    manager.loop_processes()
