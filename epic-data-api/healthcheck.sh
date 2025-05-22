#!/bin/bash
set -e

# Check if the Django application is running by making a request to localhost
curl --fail http://localhost:8000/ || exit 1

exit 0 