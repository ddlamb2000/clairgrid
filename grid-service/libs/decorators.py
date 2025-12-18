'''
    clairgrid : data structuration, presentation and navigation.
    Copyright David Lambert 2025

    This file contains the decorator for echoing function calls.
'''

import functools

def echo(func):
    """
    Decorator that prints the name of the function being called.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"{func.__name__}()", end= " ",flush=True)
        return func(*args, **kwargs)
    return wrapper