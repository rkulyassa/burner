from typing import Callable, TypeVar, Any
from functools import wraps
from time import time

T = TypeVar("T")


def measure(func: Callable[..., T]) -> Callable[..., T]:
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> T:
        print(f"{func.__name__} called")
        start_time = time()
        result = func(*args, **kwargs)
        end_time = time()
        print(f"{func.__name__} took {end_time - start_time:.4f}s")
        return result

    return wrapper


# can be provided as an option in the future
restricted_chars = [".", ","]


def filter_chars(input: str) -> str:
    return "".join([c if c not in restricted_chars else "" for c in input])
