#!/bin/bash

pypy3 purge_test_database.py
pytest tests/unit
pytest tests/system # -o log_cli=true -o log_cli_level=INFO

if [ -n "$KEEP_ALIVE_AFTER_SECONDS" ]; then
    echo "Keeping alive for $KEEP_ALIVE_AFTER_SECONDS seconds."
    sleep $KEEP_ALIVE_AFTER_SECONDS
fi