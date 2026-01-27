import csv
import gzip
import json
import logging
import os
import shutil
from datetime import datetime
from typing import List, Set

from fastapi import UploadFile

from log import ManagerInterface

SABIN_DIR = os.getenv("SABIN_DATA_DIR", "/data/sabin")
SABIN_SENT_FILES = os.path.join(SABIN_DIR, "sent_files.txt")
REQUIRED_COLUMNS = [
    "OS",
    "CodigoPosto",
    "Estado",
    "Municipio",
    "DataAtendimento",
    "DataNascimento",
    "Sexo",
    "Descricao",
    "Parametro",
    "Resultado",
    "DataAssinatura",
]


def ensure_sabin_dir():
    os.makedirs(SABIN_DIR, exist_ok=True)


def save_sabin_gzip_upload(upload_file: UploadFile) -> str:
    """
    Persist uploaded gzip CSV to disk without loading it in memory.

    Returns:
        str: Saved filename.
    """

    ensure_sabin_dir()
    now = datetime.now()
    filename = f"sabin_{now.strftime('%Y-%m-%d_%H-%M-%S')}_{int(now.microsecond/1000):03d}.csv.gz"
    file_path = os.path.join(SABIN_DIR, filename)

    with open(file_path, "wb") as dest:
        shutil.copyfileobj(upload_file.file, dest, length=1024 * 1024)

    # Lightweight validation: ensure required headers exist
    try:
        validate_csv_header(file_path)
    except Exception:
        os.remove(file_path)
        raise

    return filename


def save_sabin_csv_bytes(data: bytes) -> str:
    """
    Persist raw CSV bytes to disk.

    Returns:
        str: Saved filename.
    """

    ensure_sabin_dir()
    now = datetime.now()
    filename = f"sabin_{now.strftime('%Y-%m-%d_%H-%M-%S')}_{int(now.microsecond/1000):03d}.csv"
    file_path = os.path.join(SABIN_DIR, filename)

    with open(file_path, "wb") as dest:
        dest.write(data)

    try:
        validate_csv_header_plain(file_path)
    except Exception:
        os.remove(file_path)
        raise

    return filename


def validate_csv_header(file_path: str) -> None:
    """
    Validate that the CSV (gzip) contains the required columns.
    Only reads the header to avoid loading the whole file.
    """
    with gzip.open(file_path, "rt", newline="") as gz_file:
        reader = csv.DictReader(gz_file)
        fieldnames = reader.fieldnames or []
        missing = [col for col in REQUIRED_COLUMNS if col not in fieldnames]
        if missing:
            raise ValueError(f"Missing required columns: {', '.join(missing)}")


def validate_csv_header_plain(file_path: str) -> None:
    """
    Validate that the CSV (plain) contains the required columns.
    Only reads the header to avoid loading the whole file.
    """
    with open(file_path, "r", newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        fieldnames = reader.fieldnames or []
        missing = [col for col in REQUIRED_COLUMNS if col not in fieldnames]
        if missing:
            raise ValueError(f"Missing required columns: {', '.join(missing)}")


def save_sabin_data_flow(sabin_data):
    """
    Save the Sabin data to the database.

    Args:
        sabin_data (SabinDataList): The data to be saved.
    """

    # Transform SabinDataList to a list of dictionaries
    sabin_data_list = format_sabin_data_json(sabin_data)

    # Save one JSON file per timestamp with milliseconds
    now = datetime.now()
    file_name = f"sabin_{now.strftime('%Y-%m-%d_%H-%M-%S')}_{int(now.microsecond/1000):03d}.json"
    file_path = f"/data/sabin/{file_name}"

    # Save the Sabin data to a JSON file
    with open(file_path, "w") as file:
        json.dump(sabin_data_list, file, indent=4)

    # Save the Sabin data into the API
    send_sabin_files_to_server_api()

def get_manager_interface():
    """
    Retrieve the ManagerInterface instance.
    This function is a placeholder for the actual implementation.
    """

    api_endpoint = os.getenv("MANAGER_ENDPOINT")
    app_name = 'collector'

    if not api_endpoint:
        raise ValueError("API_ENPOINT is not set in the environment variables.")
    
    return ManagerInterface(app_name, api_endpoint)

def format_sabin_data_json(sabin_data):
    """
    Format Sabin data to JSON format.

    Args:
        sabin_data (SabinDataList): The data to be formatted.

    Returns:
        str: The formatted JSON string.
    """

    # Transform SabinDataList to a list of dictionaries
    data_list = [data.dict() for data in sabin_data.data]

    # DataAtendimento, DataNascimento, DataAssinatura format dd/mm/yyyy
    for data in data_list:
        data['DataAtendimento'] = data['DataAtendimento'].strftime('%Y-%m-%d')
        data['DataNascimento'] = data['DataNascimento'].strftime('%Y-%m-%d')
        data['DataAssinatura'] = data['DataAssinatura'].strftime('%Y-%m-%d')

    return data_list

def list_sabin_sent_files():
    """
    List the files that have been sent to the server API.
    """

    if os.path.exists(SABIN_SENT_FILES):
        with open(SABIN_SENT_FILES, "r") as file:
            return file.read().splitlines()
    return []

def add_file_to_sent_list(filename):
    """
    Add a file to the list of sent files.
    
    Args:
        filename (str): The name of the file to be added.
    """

    with open(SABIN_SENT_FILES, "a") as file:
        file.write(f"{filename}\n")

def send_sabin_files_to_server_api():
    """
    Send the Sabin data files to the server API.
    """

    try:
        manager_interface = get_manager_interface()
    except Exception as exc:
        logging.exception("Unable to create ManagerInterface.")
        return

    logger = manager_interface.logger

    ensure_sabin_dir()
    all_sabin_files = os.listdir(SABIN_DIR)
    sent_files: Set[str] = set(list_sabin_sent_files())

    for filename in all_sabin_files:
        if (
            filename in sent_files
            or not filename.startswith("sabin_")
            or not filename.endswith(".csv.gz")
        ):
            continue

        file_path = os.path.join(SABIN_DIR, filename)
        if not os.path.isfile(file_path):
            continue

        logger.info(f"Sending file {filename} to server API...")
        with open(file_path, "rb") as file_content:
            try:
                manager_interface.upload_file(
                    organization="sabin",
                    project="arbo",
                    file_content=file_content,
                    file_name=filename,
                    content_type="application/gzip",
                )
                logger.info(f"File {filename} sent to 'arbo' project.")
                file_content.seek(0)
                manager_interface.upload_file(
                    organization="sabin",
                    project="respat",
                    file_content=file_content,
                    file_name=filename,
                    content_type="application/gzip",
                )
                logger.info(f"File {filename} sent to 'respat' project.")
            except Exception as exc:
                logger.exception(f"Failed to upload {filename}.")
                continue

        logger.info(f"Adding file {filename} to sent files list.")
        add_file_to_sent_list(filename)
        logger.info(f"File {filename} has been sent and added to the sent files list.")
