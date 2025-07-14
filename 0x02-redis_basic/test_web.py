#!/usr/bin/env python3
"""
Expiring web cache and access counter using Redis
"""

import redis
import requests
from typing import Callable
from functools import wraps


r = redis.Redis()


def count_access(method: Callable) -> Callable:
    """
    Decorator to count accesses to a URL
    """
    @wraps(method)
    def wrapper(url: str) -> str:
        r.incr(f"count:{url}")
        return method(url)
    return wrapper


def cache_page(method: Callable) -> Callable:
    """
    Decorator to cache the page result for 10 seconds
    """
    @wraps(method)
    def wrapper(url: str) -> str:
        cached = r.get(f"cached:{url}")
        if cached:
            return cached.decode("utf-8")
        html = method(url)
        r.setex(f"cached:{url}", 10, html)
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
