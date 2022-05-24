import datetime
import os

from psycopg2.extras import RealDictCursor
from transfer.manager import Manager
from transfer.settings import Settings

if __name__ == '__main__':
    m = Manager()
    # промежуток времени
    # ограничение размера запроса в postgres
    settings = Settings(
        qs_limit=int(os.environ.get('query_limit', '5000')),
        dbname=os.environ.get('DB_NAME'),
        user=os.environ.get('DB_USER'),
        password=os.environ.get('DB_PASSWORD'),
        host=os.environ.get('DB_HOST', '127.0.0.1'),
        port=os.environ.get('DB_PORT', 5432),
        cursor_factory=RealDictCursor,
        date_end=datetime.datetime.now()
    )

    # самое старое обновление
    settings.date_start = settings.get_the_earliest_update()

    counter = 0
    while True:

        is_done_table, is_done_time = m.start(
            reference_date_start=settings.date_start,
            reference_date_end=settings.date_end,
            query_limit=settings.qs_limit,
            offset=settings.qs_limit * counter
        )

        if is_done_time:
            settings.date_start = settings.date_end
            settings.date_end = datetime.datetime.now()

        counter = 0 if is_done_table else counter + 1
