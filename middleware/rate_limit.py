import asyncio
import time
from functools import wraps


def rate_limit(calls: int, period: float):

    last_call = 0

    def decorator(func):

        @wraps(func)
        async def wrapper(*args, **kwargs):

            nonlocal last_call

            elapsed = time.monotonic() - last_call

            if elapsed < period:
                await asyncio.sleep(period - elapsed)

            last_call = time.monotonic()

            return await func(*args, **kwargs)

        return wrapper

    return decorator