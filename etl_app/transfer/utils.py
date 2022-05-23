import logging
import os
import time
from contextlib import contextmanager
from typing import Type

from psycopg2 import connect, extensions


def backoff(timeout_restriction: int, time_factor: int, exception: Type[BaseException] = Exception):
    def decor(func):
        def wrapper(*args, **kwargs):
            counter = 1
            while True:
                try:
                    result = func(*args, **kwargs)
                    break
                except exception as e:
                    if os.environ.get('DEBUG', "True") == 'True':
                        raise e from e
                    logging.error(e)
                    downtime = time_factor ** counter
                    if downtime > timeout_restriction:
                        downtime = timeout_restriction
                    time.sleep(downtime)
            return result
        return wrapper
    return decor


@contextmanager
def postgres_connection(*args, **kwargs) -> extensions.connection:
    conn = connect(*args, **kwargs)
    yield conn
    conn.commit()
    conn.close()
