#!/usr/bin/env python3
"""
Defines a Cache class for storing and retrieving data from Redis
"""

import redis
import uuid
from typing import Union, Callable, Optional


class Cache:
    def __init__(self):
        """Initialize Redis client and flush database"""
        self._redis = redis.Redis()
        self._redis.flushdb()

    def store(self, data: Union[str, bytes, int, float]) -> str:
        """
        Store data in Redis using a randomly generated key

        Args:
            data (Union[str, bytes, int, float]): Data to store

        Returns:
            str: The generated key
        """
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def get(self, key: str, fn: Optional[Callable] = None) -> Union[bytes, str, int, None]:
        """
        Retrieve data from Redis and optionally convert it using fn

        Args:
            key (str): Redis key
            fn (Callable, optional): Function to convert the data

        Returns:
            Original value or None if key not found
        """
        value = self._redis.get(key)
        if value is None:
            return None
        return fn(value) if fn else value

    def get_str(self, key: str) -> Optional[str]:
        """
        Retrieve a string from Redis

        Args:
            key (str): Redis key

        Returns:
            str or None
        """
        return self.get(key, fn=lambda d: d.decode("utf-8"))

    def get_int(self, key: str) -> Optional[int]:
        """
        Retrieve an integer from Redis

        Args:
            key (str): Redis key

        Returns:
            int or None
        """
        return self.get(key, fn=int)
