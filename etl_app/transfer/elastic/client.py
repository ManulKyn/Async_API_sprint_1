import os
from typing import Iterator

from elasticsearch import Elasticsearch, helpers


class EsManagement:
    def __init__(self):

        self.es_client = Elasticsearch(hosts=[f'http://{os.environ.get("ELASTICSEARCH_HOST", "localhost")}:9200'], )
        self.index = 'movies'
        self.__set_indexes()

    def __set_indexes(self):
        settings = {
            "settings": {
                "refresh_interval": "1s",
                "analysis": {
                    "filter": {
                        "english_stop": {
                            "type": "stop",
                            "stopwords": "_english_"
                        },
                        "english_stemmer": {
                            "type": "stemmer",
                            "language": "english"
                        },
                        "english_possessive_stemmer": {
                            "type": "stemmer",
                            "language": "possessive_english"
                        },
                        "russian_stop": {
                            "type": "stop",
                            "stopwords": "_russian_"
                        },
                        "russian_stemmer": {
                            "type": "stemmer",
                            "language": "russian"
                        }
                    },
                    "analyzer": {
                        "ru_en": {
                            "tokenizer": "standard",
                            "filter": [
                                "lowercase",
                                "english_stop",
                                "english_stemmer",
                                "english_possessive_stemmer",
                                "russian_stop",
                                "russian_stemmer"
                            ]
                        }
                    }
                }
            }
        }
        if not self.es_client.indices.exists(index=self.index):
            self.create_index(
                index_name=self.index,
                mapping={
                    **settings,
                    "mappings": {
                        "dynamic": "strict",
                        "properties": {
                            "id": {
                                "type": "keyword"
                            },
                            "imdb_rating": {
                                "type": "float"
                            },
                            "genre": {
                                "type": "keyword"
                            },
                            "title": {
                                "type": "text",
                                "analyzer": "ru_en",
                                "fields": {
                                    "raw": {
                                        "type": "keyword"
                                    }
                                }
                            },
                            "description": {
                                "type": "text",
                                "analyzer": "ru_en"
                            },
                            "director": {
                                "type": "text",
                                "analyzer": "ru_en"
                            },
                            "actors_names": {
                                "type": "text",
                                "analyzer": "ru_en"
                            },
                            "writers_names": {
                                "type": "text",
                                "analyzer": "ru_en"
                            },
                            "actors": {
                                "type": "nested",
                                "dynamic": "strict",
                                "properties": {
                                    "id": {
                                        "type": "keyword"
                                    },
                                    "name": {
                                        "type": "text",
                                        "analyzer": "ru_en"
                                    }
                                }
                            },
                            "writers": {
                                "type": "nested",
                                "dynamic": "strict",
                                "properties": {
                                    "id": {
                                        "type": "keyword"
                                    },
                                    "name": {
                                        "type": "text",
                                        "analyzer": "ru_en"
                                    }
                                }
                            }
                        }
                    }
                }
            )
        if not self.es_client.indices.exists(index='genres'):
            self.create_index(
                index_name='genres',
                mapping={
                    **settings,
                    "mappings": {
                        "dynamic": "strict",
                        "properties": {
                            "id": {
                                "type": "keyword"
                            },
                            "name": {
                                "type": "keyword"
                            }
                        }
                    }
                }
            )

    def create_index(self, index_name: str, mapping: dict):
        if not self.es_client.indices.exists(index=index_name):
            self.es_client.indices.create(index=index_name, body=mapping)

    def upsert(self, index, query_set: Iterator[dict]):
        actions = []
        for row in query_set:
            id_ = row.get('id')
            actions.append({
                "_op_type": 'update',
                "_index": index,
                "_id": id_,
                "doc": row,
                "doc_as_upsert": True
            })
        helpers.bulk(self.es_client, actions=actions, index=index)
        return actions
