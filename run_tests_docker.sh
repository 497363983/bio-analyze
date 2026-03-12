#!/bin/bash
if [ -z "$1" ]; then
    docker-compose -f docker-compose.test.yml run --rm bio-analyze-test packages
else
    docker-compose -f docker-compose.test.yml run --rm bio-analyze-test "$@"
fi
