#!/bin/bash

# Run health checks
python /app/healthcheck/check.py

# Check if the health check passed
if [ $? -eq 0 ]; then
  echo "Info Dengue Extractor Starting"

  python /app/main.py

else
  echo "Health checks failed. Exiting."
  exit 1
fi
