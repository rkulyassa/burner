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
