from functools import wraps


def retry(func):

    @wraps(func)
    async def wrapper(*args, **kwargs):

        last_exception = None

        for _ in range(3):

            try:
                return await func(*args, **kwargs)

            except Exception as e:
                last_exception = e

        raise last_exception

    return wrapper