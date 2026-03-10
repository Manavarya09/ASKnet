#!/bin/bash

# Wait for database to be ready
if [ -n "$DATABASE_URL" ]; then
    echo "Waiting for database..."
    until pg_isready -h postgres -p 5432 -U asknet; do
        sleep 1
    done
    echo "Database ready."
fi

# Set Python path to include ASKNet
export PYTHONPATH=/app/ASKNet:/app

# Start the FastAPI app
cd /app
exec uvicorn ASKNet.api.main:app --host 0.0.0.0 --port 80 --log-level ${LOG_LEVEL:-info}