import os
import sys

import requests
from http import HTTPStatus

def manager_api_is_reachable():
    # Get environment variables
    endpoint   = os.getenv("MANAGER_ENDPOINT")
    if not endpoint:
        return False, "Missing MANAGER_ENDPOINT. Check the .env file."

    try:
        response = requests.get(endpoint)
        if response.status_code == HTTPStatus.OK:
            return True, "Manager API is OK."
        else:
            return False, "Manager endpoint is not reachable"
    except Exception as e:
        return False, f"Exception during request {e}"


def healthcheck():
    # Run multiple health checks
    checks = {
        "Manager API is Reachable": manager_api_is_reachable    
    }

    all_healthy = True
    for name, check in checks.items():
        healthy, message = check()
        if not healthy:
            print(f"{name} FAILED: {message}")
            all_healthy = False
        else:
            print(f"{name}: {message}")

    if all_healthy:
        sys.exit(0)  # Healthy
    else:
        sys.exit(1)  # Unhealthy

if __name__ == "__main__":
    healthcheck()