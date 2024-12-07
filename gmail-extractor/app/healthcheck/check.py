import os
import sys
import json

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
    
def gmail_env_variables_are_set():
    gmail_env_variables = [
        "EMAIL_ADDRESS",
        "EMAIL_APP_PASSWORD"
    ]

    missing_vars = []

    for gmail_env_var in gmail_env_variables:
        if not os.getenv(gmail_env_var):
            missing_vars.append(gmail_env_var)

    if missing_vars:
        return False, f"The following env variables are not set in .env: {','.join(missing_vars)}"
    return True, "Able to read GMail env variables"
    
def emails_json_is_correctly_defined():
    emails_json_path = '/app/emails.json'
    
    # Verifica se o arquivo existe
    if not os.path.exists(emails_json_path):
        return False, f"File {emails_json_path} does not exist. Create a file emails.json using the emails-example.json as a model."
    
    try:
        # Verifica se o conteúdo do arquivo é um JSON válido
        with open(emails_json_path, 'r') as file:
            json.load(file)
        return True, "emails.json is correctly defined."
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON format in {emails_json_path}: {e}"
    except Exception as e:
        return False, f"Error while reading {emails_json_path}: {e}"
    
def healthcheck():
    # Run multiple health checks
    checks = {
        "Manager API is Reachable": manager_api_is_reachable,
        "GMail env variables": gmail_env_variables_are_set,
        "emails.json is defined": emails_json_is_correctly_defined
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