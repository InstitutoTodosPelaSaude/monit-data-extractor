import logging
import json
import io
import requests
import os
from datetime import datetime

import time

import pandas as pd

class JSONFormatter(logging.Formatter):
    def format(self, record):
        # Create a dictionary representation of the log record
        log_record = {
            'timestamp': self.formatTime(record),
            'level': record.levelname,
            'message': record.getMessage(),
        }
        return log_record

class APILogHandler(logging.Handler):
    def __init__(self, endpoint, session_id, app_name):
        super().__init__()
        self.endpoint = endpoint
        self.session_id = session_id
        self.app_name   = app_name

    def emit(self, record):
        # Create a log message
        log_entry = self.format(record)
        # Send the log message to the specified API endpoint
        log_entry['session_id'] = self.session_id
        log_entry['app_name']   = self.app_name

        try:
            response = requests.post(f"{self.endpoint}/log", json=log_entry)
            response.raise_for_status()  # Raise an error for bad responses
        except Exception as e:
            print(f"Failed to send log to API: {e}")

logging.basicConfig(
    level=logging.DEBUG,  # Set the minimum logging level
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Log message format
)

logger = logging.getLogger("EXAMPLE-EXTRACTOR")  # Create a logger

if __name__ == "__main__":
    API_ENPOINT = os.getenv("MANAGER_ENDPOINT")
    APP_NAME    = 'example-extractor'

    logger.info("[TUTORIAL] The First step is to get a session-id. This is used to identify the current extraction run and save its logs, status")
    logger.info("[TUTORIAL] And send the extracted data files to the storage")
    logger.info("[TUTORIAL] To get a session_id, make a GET request on /log passing a ap_name to identify this data extractor")

    time.sleep(1)

    response = requests.get(f"{API_ENPOINT}/log", params={'app_name': APP_NAME})

    logger.info("Retrieving session ID.")
    session_id = response.json()['session_id']
    logger.info(f"Session id: '{session_id}'")

    logger.info(f"[TUTORIAL] The next step is to configure the APIHandler (see the code)")

    api_handler = APILogHandler(API_ENPOINT, session_id=session_id, app_name=APP_NAME)
    json_formatter = JSONFormatter()
    api_handler.setFormatter(json_formatter)

    logger.addHandler(api_handler)

    logger.info("[TUTORIAL] Now, all the messages are automatically sent to the API and stored in the Log's database")
    logger.info("[TUTORIAL] From now on, the data extractions follows up normally.")
    logger.info("[TUTORIAL] Always try to report important aspects of the system in the logs: start and end of steps, problems and alerts, etc.")

    logger.info("Extracting data from 'example-file.csv'")
    time.sleep(5)
    fake_csv_data = [
        ('Maria', 21, 'Data Engineer', 'Banana'),
        ('John', 25, 'Software Developer', 'Apple'),
        ('Alice', 30, 'Product Manager', 'Mango'),
        ('Bob', 22, 'Data Analyst', 'Orange'),
        ('Diana', 28, 'UX Designer', 'Grapes'),
        ('Eve', 35, 'Systems Administrator', 'Pineapple'),
        ('Charlie', 27, 'DevOps Engineer', 'Strawberry'),
    ]
    df_fake = pd.DataFrame(fake_csv_data, columns=['Name', 'Age', 'Job Title', 'Favorite Fruit'])
    logger.info("Finished data extraction from 'example-file.csv'")

    logger.info("Extracting data from 'example-file2.csv'")
    time.sleep(2)
    df_fake2 = df_fake.copy()
    logger.info("Finished data extraction from 'example-file2.csv'")
    logger.warning("This is a WARNING example.")
    logger.error("This is an ERROR example.")
    logger.info("Finished data extraction.")
 
    logger.info("[TUTORIAL] Now the application has all the data in memmory.")
    logger.info("[TUTORIAL] The final step is to save all the information into the BLOB storage")
    logger.info("[TUTORIAL] This is achieved through the /file route")
    logger.info("[TUTORIAL] Make a POST request sending the file, session_id, the project and organization (laboratory) the file belongs to")

    logger.info(f"Saving 'example-file.csv' using session_id='{session_id}', organization='TestOrganization' and project='TestProject'")
    buffer = io.BytesIO()
    df_fake.to_csv(buffer, index=False)
    buffer.seek(0)  # Move to the beginning of the buffer

    response = requests.post(
        f"{API_ENPOINT}/file", 
        params={
            "session_id": session_id,
            "organization": "TestOrganization",
            "project": "TestProject"
        }, 
        files={
            "file": ("example-file.csv", buffer, 'text/csv')
        }
    )

    logger.info("Finished uploading file 'example-file.csv'")
    logger.info("[TUTORIAL] Finally, update the status of the session to 'FINISHED' and set the end timestamp")
    logger.info("[TUTORIAL] making a PUT request on /status wiht the session_id ")

    response = requests.put(
        f"{API_ENPOINT}/status", 
        json = {
            "session_id": session_id,
            "status": "COMPLETED",  # New Session STATUS
            "end": datetime.now().isoformat()
        }
    )

    logger.info("Finished pipeline.")


    