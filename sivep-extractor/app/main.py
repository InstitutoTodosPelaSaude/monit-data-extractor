import requests
from bs4 import BeautifulSoup

import os
import io

# Save and handle logs
import logging
import requests
from utils import APILogHandler, JSONFormatter

from datetime import datetime

def fetch_html(url):
    """
    Makes a request to fetch the HTML content of a page.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  # Checks for request errors
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the page's HTML: {e}")
        return None

def extract_csv_public_links(html):
    """
    Extracts all links (href attributes) from the provided HTML content.
    :param html: String containing the HTML content.
    :return: List of strings with the values of href attributes.
    """
    soup = BeautifulSoup(html, 'html.parser')
    hrefs = [a.get('href') for a in soup.find_all('a', href=True, class_="dropdown-item resource-url-analytics")]
    hrefs = [ href for href in hrefs if href.endswith('.csv') ]
    return hrefs

def download_csv(url):
    """
    Downloads a CSV file from the given URL and returns its content as a BytesIO object.
    :param url: URL of the CSV file.
    :return: BytesIO object containing the CSV data.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        logging.info(f"Successfully downloaded CSV from {url}")
        return io.BytesIO(response.content)  # Convert to a file-like object
    except requests.exceptions.RequestException as e:
        logging.error(f"Error downloading CSV: {e}")
        return None
    
if __name__ == "__main__":
    datasus_url = 'https://opendatasus.saude.gov.br/dataset/srag-2021-a-2024'

    API_ENPOINT = os.getenv("MANAGER_ENDPOINT")
    APP_NAME    = 'sivep'
    
    if API_ENPOINT is None:
        print(f"ERROR! API_ENPOINT is None")
        exit(1)

    # ===================================
    # Logger configuration
    # ===================================
    
    logging.basicConfig(
        level=logging.DEBUG,  # Set the minimum logging level
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Log message format
    )
    logger = logging.getLogger(APP_NAME.upper())  # Create a logger
    response = requests.get(f"{API_ENPOINT}/log", params={'app_name': APP_NAME})

    # Application
    # ==================================
    logger.info("Starting SIVEP extractor")

    logger.info("Retrieving session ID.")
    session_id = response.json()['session_id']
    logger.info(f"Session id: '{session_id}'")

    api_handler = APILogHandler(API_ENPOINT, session_id=session_id, app_name=APP_NAME)
    json_formatter = JSONFormatter()
    api_handler.setFormatter(json_formatter)
    logger.info(f"Saving Logs in the database...")

    logger.info(f"Requesting HTML content from DATASUS page {datasus_url}")
    html_content = fetch_html(url=datasus_url)

    if not html_content:
        logger.critical(f"Unable to retrieve content from {datasus_url}")
        exit(1)

    logger.info(f"Extracting CSV file links available in the Page")
    csv_links = extract_csv_public_links(html_content)

    if not csv_links:
        logger.critical(f"Unable to found csv files in {datasus_url}")
        exit(1)

    logger.info(f"Found {len(csv_links)} files.")

    was_able_to_download_at_least_one_file = False
    for link in csv_links:
        
        logger.info(f"Saving file - {link}")
        file_content = download_csv(link)
        filename = link.split('/')[-1]

        if not file_content:
            logger.error(f"Unable to retrieve file - {link}")
            continue

        response = requests.post(
            f"{API_ENPOINT}/file", 
            params={
                "session_id": session_id,
                "organization": "SIVEP",
                "project": "respat"
            }, 
            files={
                "file": (filename, file_content, 'text/csv')
            }
        )

        logger.info(f"Successfully saved file {filename}")
        was_able_to_download_at_least_one_file = True

    if not was_able_to_download_at_least_one_file:
        logger.critical(f"Unable to retrieve any files from DATASUS")
        exit(1)

    logger.info("Finished extracting all data")

    response = requests.put(
        f"{API_ENPOINT}/status", 
        json = {
            "session_id": session_id,
            "status": "COMPLETED",  # New Session STATUS
            "end": datetime.now().isoformat()
        }
    )

    logger.info("Finished pipeline.")

    

    