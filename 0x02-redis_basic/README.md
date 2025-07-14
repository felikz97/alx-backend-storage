# 0x02. Redis basic

# Redis Basic (ALX Backend Storage)

This project demonstrates how to use Redis with Python for:

- Key/value storage
- Method call tracking using decorators
- Input/output logging
- Replay of method call history

## Features

- `store(data)` stores data in Redis with a UUID key
- `get(key, fn=None)` retrieves and optionally transforms data
- `@count_calls` counts how many times a method is called
- `@call_history` logs method inputs and outputs
- `replay(method)` prints history of calls for a method

## Usage

```python
cache = Cache()
cache.store("foo")
cache.store("bar")
replay(cache.store)

This project introduces basic usage of Redis with Python using the `redis-py` library.

## Files

- `exercise.py`: Contains the `Cache` class that interacts with Redis
- `main.py`: Sample script to test the Cache class

## Requirements

- Python 3.x
- `redis` Python package (`pip install redis`)
- Redis server running locally (`localhost:6379`)

## Usage

```bash
$ python3 main.py
