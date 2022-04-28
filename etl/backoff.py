import time
from functools import wraps


def backoff(
        start_sleep_time: float = 0.1,
        factor: int = 2,
        border_sleep_time: int = 10
):

    def func_wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            retries: int = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception:
                    sleep_time = start_sleep_time * (factor ** retries)
                    if sleep_time >= border_sleep_time:
                        sleep_time = border_sleep_time
                    time.sleep(sleep_time)
                    retries += 1

        return inner

    return func_wrapper
