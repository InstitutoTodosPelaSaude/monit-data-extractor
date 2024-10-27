#!/bin/bash

# Run health checks
python /app/healthcheck/check.py

# Check if the health check passed
if [ $? -eq 0 ]; then
  echo "Example Extractor Starting"
  echo "This is a model of how Data Extractor should be built"
  echo "Starting Data extraction for Example Lab in $(date +"%Y-%m-%d %H:%M:%S")"

  python /app/main.py
  
else
  echo "Health checks failed. Exiting."
  exit 1
fi
