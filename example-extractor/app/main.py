import io
import requests
import os
from datetime import datetime

import time
import pandas as pd
from log import ManagerInterface


if __name__ == "__main__":
    API_ENPOINT = os.getenv("MANAGER_ENDPOINT")
    APP_NAME    = 'example-extractor'
    
    manager_interface = ManagerInterface(APP_NAME, API_ENPOINT )
    logger = manager_interface.logger

    logger.info("[TUTORIAL] The First step is to createa a ManagerInterface object and retrieve the logger.")
    logger.info("[TUTORIAL] The manager interface is responsible to intermediate the communcation beteween the extractor application and the Manager API")
    logger.info("[TUTORIAL] It will be responsible for creating a logs session to send all the log messages automatically to the API (to be stored)")
    logger.info("[TUTORIAL] keep track of the app status, and uploading the extracted files to the storage")

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

    logger.info(f"Saving 'example-file.csv' using session_id='{manager_interface.session_id}', organization='TestOrganization' and project='TestProject'")
    buffer = io.BytesIO()
    df_fake.to_csv(buffer, index=False)
    buffer.seek(0)  # Move to the beginning of the buffer

    manager_interface.upload_file(
        organization="TestOrganization",
        project="TestProject",
        file_content=buffer,
        file_name="example-file.csv"
    )

    logger.info("Finished uploading file 'example-file.csv'")
    logger.info("[TUTORIAL] Finally, update the status of the session to 'FINISHED' and set the end timestamp")
    logger.info("[TUTORIAL] making a PUT request on /status wiht the session_id ")

    manager_interface.close_session()

    logger.info("Finished pipeline.")


    