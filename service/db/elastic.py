from typing import Optional
from elasticsearch import Elasticsearch

es: Optional[Elasticsearch] = None


# Функция понадобится при внедрении зависимостей
async def get_elastic() -> Elasticsearch:
    return es
