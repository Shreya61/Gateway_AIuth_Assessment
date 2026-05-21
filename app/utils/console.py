import os


def is_verbose():
    return os.getenv("AIUTHOR_VERBOSE", "").lower() in {"1", "true", "yes"}


def debug_print(*args, **kwargs):
    if is_verbose():
        print(*args, **kwargs)
