#!/usr/bin/env python3
"""
Expiring web cache and access counter using Redis
"""

import redis
import requests
from functools import wraps
from typing import Callable


r = redis.Redis()


def count_access(method: Callable) -> Callable:
    """
    Decorator to count how many times a URL was accessed
    """
    @wraps(method)
    def wrapper(url: str) -> str:
        key = f"count:{url}"
        r.incr(key)
        return method(url)
    return wrapper


def cache_page(method: Callable) -> Callable:
    """
    Decorator to cache the HTML content of a URL for 10 seconds
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
    Fetch and cache the HTML content of a URL

    Args:
        url (str): The URL to fetch

    Returns:
        str: The HTML content of the page
    """
    response = requests.get(url)
    return response.text


if __name__ == "__main__":
    import time

    url = "http://slowwly.robertomurray.co.uk"

    print("1. Fetching URL (should be slow)...")
    html = get_page(url)
    print(f"Length: {len(html)}")
    print("Cached:", bool(r.get(f"cached:{url}")))
    print("Access count:", r.get(f"count:{url}").decode())

    print("\n2. Fetching again (should be cached)...")
    html = get_page(url)
    print(f"Length: {len(html)}")
    print("Cached:", bool(r.get(f"cached:{url}")))
    print("Access count:", r.get(f"count:{url}").decode())

    print("\nWaiting 11 seconds for cache to expire...")
    time.sleep(11)

    print("\n3. Fetching after cache expiry (should be slow)...")
    html = get_page(url)
    print(f"Length: {len(html)}")
    print("Cached:", bool(r.get(f"cached:{url}")))
    print("Access count:", r.get(f"count:{url}").decode())
