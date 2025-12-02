#!/bin/bash

echo "clairgrid test starting."

pytest tests/test_grid_service.py

echo "clairgrid test completed."

if [ -n "$KEEP_ALIVE_AFTER_SECONDS" ]; then
    echo "clairgrid test keeping alive for $KEEP_ALIVE_AFTER_SECONDS seconds."
    sleep $KEEP_ALIVE_AFTER_SECONDS
fi

echo "clairgrid test ended."
