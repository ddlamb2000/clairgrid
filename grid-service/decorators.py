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

def validate_jwt(func):
    """
    Decorator that checks for valid JWT before executing the function.
    Assumes the first argument is 'self' (QueueListener instance) and the second is 'request'.
    """
    @functools.wraps(func)
    def wrapper(self, request, *args, **kwargs):
        validation_error = self._handle_jwt_validation(request)
        if validation_error:
            return validation_error
        return func(self, request, *args, **kwargs)
    return wrapper
