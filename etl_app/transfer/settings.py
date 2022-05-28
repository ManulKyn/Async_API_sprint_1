import datetime
from typing import Optional

from psycopg2.extras import RealDictCursor
from pydantic import BaseModel, Field

from .utils import backoff, postgres_connection


class Settings(BaseModel):
    qs_limit: int = Field(default=5000)
    dbname: str
    user: str
    password: str
    host: str = Field(default='127.0.01')
    port: int = Field(default=5432)
    cursor_factory = Field(default=RealDictCursor)
    date_end: datetime.datetime = Field(default_factory=datetime.datetime.now)
    date_start: Optional[datetime.datetime]

    @backoff(timeout_restriction=180, time_factor=2)
    def get_the_earliest_update(self) -> datetime.datetime:
        with postgres_connection(
                dbname=self.dbname,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port,
                cursor_factory=self.cursor_factory,
        ) as conn, conn.cursor(cursor_factory=self.cursor_factory) as cur:
            cur.execute(
                """
                -- если нет дат, то таблицы пустые и начинаем смотреть с текущей даты
                select min(coalesce(fw.modified, g.modified, p.modified, now())) earliest_date from content.film_work fw 
                full outer join "content".genre g on g.modified = fw.modified 
                full outer join "content".person p  on p.modified = fw.modified;
                """
            )
            earliest = cur.fetchone()
        return earliest['earliest_date']
