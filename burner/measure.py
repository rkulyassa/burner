import time
from functools import wraps

# t_0 = time.time()
# t_1 = time.time()
# print(f"{(t_1-t_0):.4f}s")


def measure(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"{func.__name__} called")
        start_time = time.time()  # Record the start time
        result = func(*args, **kwargs)  # Execute the function
        end_time = time.time()  # Record the end time
        print(f"{func.__name__} took {end_time - start_time:.4f}s")
        return result

    return wrapper
