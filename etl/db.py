from typing import List, Dict, Any
from dataclasses import dataclass

import psycopg2

from backoff import backoff


@dataclass
class PostgresDatabase:
    url: str

    @backoff()
    def query(self, template: str, params: Dict[str, Any]) -> List[dict]:
        results = []
        with psycopg2.connect(self.url) as connection:
            with connection.cursor(
                    cursor_factory=psycopg2.extras.RealDictCursor
            ) as cursor:
                cursor.execute(template, params)
                results = [dict(r) for r in cursor.fetchall()]
        return results
