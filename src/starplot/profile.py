import time


def profile(func):
    def wrapper(*args, **kwargs):
        start = time.time()

        result = func(*args, **kwargs)

        duration = round(time.time() - start, 4)

        args[0].logger.debug(f"{func.__name__} = {str(duration)} sec")

        return result

    return wrapper
