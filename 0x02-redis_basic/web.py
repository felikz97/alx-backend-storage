#!/usr/bin/env python3
"""
Web cache and tracker using Redis
"""

import redis
import requests
from functools import wraps
from typing import Callable


# Redis connection
r = redis.Redis()


def count_access(method: Callable) -> Callable:
    """
    Decorator to count how many times a URL was accessed
    """
    @wraps(method)
    def wrapper(url: str) -> str:
        r.incr(f"count:{url}")
        return method(url)
    return wrapper


def cache_page(method: Callable) -> Callable:
    """
    Decorator to cache the page content for 10 seconds
    """
    @wraps(method)
    def wrapper(url: str) -> str:
        cached = r.get(f"cached:{url}")
        if cached:
            return cached.decode("utf-8")

        html = method(url)
        # Cache the result for 10 seconds
        r.setex(f"cached:{url}", 10, html)
        return html
    return wrapper


@count_access
@cache_page
def get_page(url: str) -> str:
    """
    Fetch HTML content from the given URL.

    Args:
        url (str): The target URL

    Returns:
        str: HTML content of the URL
    """
    response = requests.get(url)
    return response.text
