import json
import os
from io import BytesIO
from datetime import datetime

from log import ManagerInterface

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

    sent_files = []
    sent_files_path = "/data/sabin/sent_files.txt"

    if os.path.exists(sent_files_path):
        with open(sent_files_path, "r") as file:
            sent_files = file.read().splitlines()

    return sent_files

def add_file_to_sent_list(filename):
    """
    Add a file to the list of sent files.
    
    Args:
        filename (str): The name of the file to be added.
    """

    sent_files_path = "/data/sabin/sent_files.txt"
    
    with open(sent_files_path, "a") as file:
        file.write(f"{filename}\n")

def send_sabin_files_to_server_api():
    """
    Send the Sabin data files to the server API.
    """

    manager_interface = get_manager_interface()
    logger = manager_interface.logger

    all_sabin_files = os.listdir("/data/sabin")
    sent_files = list_sabin_sent_files()

    for filename in all_sabin_files:
        if filename in sent_files:
            continue
        
        if not filename.startswith('sabin_') or not filename.endswith('.json'):
            continue

        logger.info(f"Sending file {filename} to server API...")
        file_content = BytesIO(open(f"/data/sabin/{filename}", "rb").read())
    
        # [WIP] Upload files to both 'arbo' and 'respat' projects
        manager_interface.upload_file(
            organization='sabin',
            project='arbo',
            file_content=file_content,
            file_name=filename
        )
        logger.info(f"File {filename} sent to 'arbo' project.")

        manager_interface.upload_file(
            organization='sabin',
            project='respat',
            file_content=file_content,
            file_name=filename
        )
        logger.info(f"File {filename} sent to 'respat' project.")

        logger.info(f"Adding file {filename} to sent files list.")
        add_file_to_sent_list(filename)
        logger.info(f"File {filename} has been sent and added to the sent files list.")
