#!/bin/bash

pytest unit
pytest system # -o log_cli=true -o log_cli_level=INFO

if [ -n "$KEEP_ALIVE_AFTER_SECONDS" ]; then
    echo "Keeping alive for $KEEP_ALIVE_AFTER_SECONDS seconds."
    sleep $KEEP_ALIVE_AFTER_SECONDS
fi