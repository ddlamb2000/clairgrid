#!/bin/bash

echo "Test starting."
python3 -m pytest
echo "Test completed."

if [ -n "$KEEP_ALIVE_AFTER_SECONDS" ]; then
    echo "clairgrid test keeping alive for $KEEP_ALIVE_AFTER_SECONDS seconds."
    sleep $KEEP_ALIVE_AFTER_SECONDS
fi

echo "Test ended."
