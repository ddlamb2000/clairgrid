'''
    clairgrid : data structuration, presentation and navigation.
    Copyright David Lambert 2025

    This file contains the function to print a stack trace.
'''

import inspect

def report_exception(exception, message = None):
    if message:
        print(f"❌ {message} due to exception '{exception}'", end=" ")
        stacktrace = exception.__traceback__
        for frame in inspect.getinnerframes(stacktrace):
            filename = frame.filename
            lineno = frame.lineno
            function = frame.function
            print(f"; file = \"{filename}\", line {lineno}, in {function}", end=" ")
            code_context = frame.code_context
            code_context = code_context[0].strip() if code_context else "No code context"
            print(f" ; code = \"{code_context}\"", flush=True)

    else:
        print(f"❌ Exception '{exception}'", flush=True)