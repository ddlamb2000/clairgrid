#!/bin/bash

docker exec -it clairgrid-grid-service-development pypy3 purge_test_database.py
docker exec -it clairgrid-grid-service-development pytest tests/unit
docker exec -it clairgrid-grid-service-development pytest tests/system