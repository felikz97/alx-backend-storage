#!/usr/bin/env python3
"""
Web cache using Redis: count access and expire cache after 10 seconds.
"""

import redis
import requests
from functools import wraps
from typing import Callable

r = redis.Redis()


def count_access(method: Callable[[str], str]) -> Callable[[str], str]:
    """Decorator to count how many times a URL is accessed."""
    @wraps(method)
    def wrapper(url: str) -> str:
        count_key = f"count:{url}"
        r.incr(count_key)
        return method(url)
    return wrapper


def cache_result(method: Callable[[str], str]) -> Callable[[str], str]:
    """Decorator to cache the HTML content for 10 seconds."""
    @wraps(method)
    def wrapper(url: str) -> str:
        cache_key = f"cache:{url}"
        cached = r.get(cache_key)
        if cached:
            return cached.decode("utf-8")
        result = method(url)
        r.setex(cache_key, 10, result)
        return result
    return wrapper


@count_access
@cache_result
def get_page(url: str) -> str:
    """
    Fetches and returns HTML content of a given URL.
    Uses Redis to cache for 10 seconds and tracks access count.

    Args:
        url (str): The URL to fetch.

    Returns:
        str: HTML content.
    """
    return requests.get(url).text


if __name__ == "__main__":
    import time

    url = "http://google.com"
    print("Calling get_page...")
    html = get_page(url)
    print("Length of content:", len(html))
    print("Cache exists:", r.exists(f"cache:{url}"))
    print("Access count:", int(r.get(f"count:{url}")))

    print("\nCalling get_page again (should be cached)...")
    html = get_page(url)
    print("Access count:", int(r.get(f"count:{url}")))

    print("\nSleeping for 11 seconds (cache expires)...")
    time.sleep(11)

    print("\nCalling get_page again (cache should be gone)...")
    html = get_page(url)
    print("Cache exists:", r.exists(f"cache:{url}"))
    print("Access count:", int(r.get(f"count:{url}")))
