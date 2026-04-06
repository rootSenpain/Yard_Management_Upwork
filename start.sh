#!/bin/bash
set -e

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready on db:5432..."

# Loop until 'db' host and port 5432 are reachable
while ! nc -z db 5432; do
  sleep 0.5
done

echo "PostgreSQL is up - executing database migrations..."

# 1. Run database migrations (Alembic)
alembic upgrade head

# 2. Load initial seed data
echo "PostgreSQL is up - loading initial seed data..."
python -m app.core.seed

# 3. Start the FastAPI application
echo "Starting FastAPI application with Uvicorn..."
exec uvicorn app.main:socket_app --host 0.0.0.0 --port 8000