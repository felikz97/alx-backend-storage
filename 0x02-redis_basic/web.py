#!/usr/bin/env python3
"""
Expiring web cache and access counter using Redis.
Tracks number of times a URL is accessed and caches content
for 10 seconds before expiring the key.
"""

import redis
import requests
from functools import wraps
from typing import Callable


# Initialize Redis client
r = redis.Redis()


def count_access(method: Callable[[str], str]) -> Callable[[str], str]:
    """
    Decorator to count how many times a URL was accessed.

    Args:
        method (Callable): The method to wrap.

    Returns:
        Callable: The wrapped method with counting logic.
    """
    @wraps(method)
    def wrapper(url: str) -> str:
        key = f"count:{url}"
        r.incr(key)
        return method(url)
    return wrapper


def cache_page(method: Callable[[str], str]) -> Callable[[str], str]:
    """
    Decorator to cache the HTML content of a URL in Redis for 10 seconds.

    Args:
        method (Callable): The method to wrap.

    Returns:
        Callable: The wrapped method with caching logic.
    """
    @wraps(method)
    def wrapper(url: str) -> str:
        key = f"cached:{url}"
        cached = r.get(key)
        if cached:
            return cached.decode("utf-8")
        html = method(url)
        r.setex(key, 10, html)
        return html
    return wrapper


@count_access
@cache_page
def get_page(url: str) -> str:
    """
    Fetch and return the HTML content of a URL.

    If the URL is cached, return the cached result.
    Otherwise, perform a web request, cache it, and return the result.

    Args:
        url (str): The target URL.

    Returns:
        str: The HTML content of the page.
    """
    response = requests.get(url)
    return response.text


if __name__ == "__main__":
    import time

    url = "http://google.com"

    print("=== Test Case: Redis Web Cache ===\n")

    print("1. Fetching URL (should hit network)...")
    html = get_page(url)
    print(f"Length of content: {len(html)}")
    print("Cached:", bool(r.get(f"cached:{url}")))
    print("Access count:", r.get(f"count:{url}").decode())

    print("\n2. Fetching again within 10 seconds (should be cached)...")
    html = get_page(url)
    print(f"Length of content: {len(html)}")
    print("Cached:", bool(r.get(f"cached:{url}")))
    print("Access count:", r.get(f"count:{url}").decode())

    print("\nWaiting 11 seconds for cache to expire...")
    time.sleep(11)

    print("\n3. Fetching after cache expiry (should hit network again)...")
    html = get_page(url)
    print(f"Length of content: {len(html)}")
    print("Cached:", bool(r.get(f"cached:{url}")))
    print("Access count:", r.get(f"count:{url}").decode())

    print("\n=== End of Test ===")

class Cache:
    """
    Cache class interfacing with Redis to store data and track usage.
    """
    def __init__(self):
        self._redis = redis.Redis()

    @count_access
    @cache_page
    def store(self, data: str) -> str:
        """
        Store data in Redis and return it.

        Args:
            data (str): The data to store.

        Returns:
            str: The stored data.
        """
        key = f"data:{data}"
        self._redis.set(key, data)
        return data
