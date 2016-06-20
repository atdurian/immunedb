#!/bin/bash
export API_ENDPOINT=${API_ENDPOINT:-http://localhost:5000}
export BASE_URL=${BASE_URL:-http://localhost:8080}
export DB_VOLUME=${DB_VOLUME:-~/immunedb/db}
export DATA_VOLUME=${DATA_VOLUME:-~/immunedb/data}
export API_PORT=${API_PORT:-5000}
export SERVE_PORT=${SERVE_PORT:-8080}
export PRODUCTION=${PRODUCTION:-0}

docker-compose ${1:-up}
