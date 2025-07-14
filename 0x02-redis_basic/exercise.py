#!/usr/bin/env python3
"""
Redis-based Cache class with decorators for
call counting, input/output logging, and history replay
"""

import redis
import uuid
from typing import Union, Callable, Optional
from functools import wraps


def count_calls(method: Callable) -> Callable:
    """
    Decorator to count how many times a method is called.

    Args:
        method (Callable): The method to decorate

    Returns:
        Callable: The wrapped method
    """
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        key = method.__qualname__
        self._redis.incr(key)
        return method(self, *args, **kwargs)
    return wrapper


def call_history(method: Callable) -> Callable:
    """
    Decorator to log the history of inputs and outputs of method calls.

    Args:
        method (Callable): The method to decorate

    Returns:
        Callable: The wrapped method
    """
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        input_key = f"{method.__qualname__}:inputs"
        output_key = f"{method.__qualname__}:outputs"

        self._redis.rpush(input_key, str(args))
        result = method(self, *args, **kwargs)
        self._redis.rpush(output_key, str(result))

        return result
    return wrapper


def replay(method: Callable) -> None:
    """
    Display the history of calls of a method.

    Args:
        method (Callable): The method whose history to display
    """
    r = method.__self__._redis
    name = method.__qualname__

    inputs = r.lrange(f"{name}:inputs", 0, -1)
    outputs = r.lrange(f"{name}:outputs", 0, -1)

    print(f"{name} was called {len(inputs)} times:")
    for inp, out in zip(inputs, outputs):
        print(f"{name}(*{inp.decode('utf-8')}) -> {out.decode('utf-8')}")


class Cache:
    """
    Cache class interfacing with Redis to store data and track usage
    """

    def __init__(self):
        """
        Initialize Redis connection and flush the DB
        """
        self._redis = redis.Redis()
        self._redis.flushdb()

    @call_history
    @count_calls
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """
        Store data in Redis under a randomly generated key

        Args:
            data (Union[str, bytes, int, float]): The data to store

        Returns:
            str: The generated key
        """
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def get(self,
            key: str,
            fn: Optional[Callable] = None
            ) -> Union[bytes, str, int, None]:
        """
        Retrieve data from Redis and optionally apply a conversion function

        Args:
            key (str): The Redis key
            fn (Callable, optional): A function to convert the data

        Returns:
            Union[bytes, str, int, None]: Retrieved data
        """
        value = self._redis.get(key)
        if value is None:
            return None
        return fn(value) if fn else value

    def get_str(self, key: str) -> Optional[str]:
        """
        Retrieve a UTF-8 decoded string from Redis

        Args:
            key (str): Redis key

        Returns:
            Optional[str]: Decoded string or None
        """
        return self.get(key, fn=lambda d: d.decode("utf-8"))

    def get_int(self, key: str) -> Optional[int]:
        """
        Retrieve an integer from Redis

        Args:
            key (str): Redis key

        Returns:
            Optional[int]: Integer or None
        """
        return self.get(key, fn=int)
