#!/bin/bash

echo "Test starting."
python3 -m pytest unit
python3 -m pytest system
echo "Test completed."

if [ -n "$KEEP_ALIVE_AFTER_SECONDS" ]; then
    echo "clairgrid test keeping alive for $KEEP_ALIVE_AFTER_SECONDS seconds."
    sleep $KEEP_ALIVE_AFTER_SECONDS
fi

echo "Test ended."
