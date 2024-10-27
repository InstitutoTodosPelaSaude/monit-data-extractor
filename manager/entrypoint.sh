#!/bin/bash

# Run health checks
python /app/healthcheck/check.py

# Check if the health check passed
if [ $? -eq 0 ]; then
  echo "Health checks passed. Starting Application..."

  python /app/create_database.py
  python /app/models.py

  echo "Notifier application started - CRON in background"
  cron

  # Start API
  uvicorn main:app --reload --host 0.0.0.0 --port 8000
else
  echo "Health checks failed. Exiting."
  exit 1
fi