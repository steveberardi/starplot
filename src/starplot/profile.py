import time


def profile(func):
    def wrapper(*args, **kwargs):
        start = time.perf_counter()

        result = func(*args, **kwargs)

        duration = int((time.perf_counter() - start) * 1_000)

        args[0].logger.debug(f"{func.__name__} = {duration}ms")

        return result

    return wrapper
