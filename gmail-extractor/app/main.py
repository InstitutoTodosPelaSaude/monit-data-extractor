import email
import imaplib

from dotenv import load_dotenv
import os
from datetime import datetime, timedelta

import json
import os
import io

# Save and handle logs
from log import ManagerInterface

def update_last_download_time():
    with open('/app/last_download_time.txt', 'w') as f:
        f.write(datetime.now().strftime('%Y-%m-%d'))
    
def last_download_time():
    try:
        with open('/app/last_download_time.txt', 'r') as f:
            return datetime.strptime(f.read(), '%Y-%m-%d')
    except Exception as e:
        return (datetime.now() - timedelta(days=30))
    
def load_emails_list():
    """Loads the e-mail list from /app/emails.json. 
    This list is a set of key-pairs, containing the lab and the list of e-mails it can use to send data.
    Ex. {'my-beautiful-lab': ['my-beautiful-lab@email.com'], 'lab-2-lab': ['user1@lab.com', 'user2@lab.com'] }

    Returns:
        dict: A dictionary representing the JSON or None.
    """
    try:
        with open('/app/emails.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        return None

def get_attachments_from_email(mail, email_id):
    """
    Extract the attachments from a specific e-mail and return as a BytesIO list.
    
    Args:
        mail (imaplib.IMAP4_SSL): Connection with IMAP Server.
        email_id (bytes): E-mail id

    Returns:
        List[Tuple[str, io.BytesIO]]: Tuple list containing the filename and binary content.
    """
    try:
        # Obtém o e-mail pelo ID
        result, data = mail.fetch(email_id, '(RFC822)')
        if result != 'OK':
            raise Exception(f"Failed to fetch email with ID {email_id}")

        # Decodifica o e-mail
        raw_email = data[0][1]
        email_message = email.message_from_bytes(raw_email)

        attachments = []
        for part in email_message.walk():
            # Verifica se o conteúdo é um anexo
            if part.get_content_disposition() == 'attachment':
                filename = part.get_filename()
                if filename:  # Apenas processa se houver nome de arquivo
                    file_data = part.get_payload(decode=True)  # Decodifica o conteúdo do anexo
                    if file_data:
                        attachments.append((filename, io.BytesIO(file_data)))

        return attachments

    except Exception as e:
        logger.error(f"Error while fetching attachments from email ID {email_id}: {e}")
        return []


def determine_project_from_file_name(lab, filename):
    """Define whether the file is part of project arbo, respat, or both from its name and origin lab.

    Args:
        lab (str): File's lab
        filename (str): The name of the file

    Returns:
        List[str]: A list of strings containg all the projects the file is part of
    """

    if lab in ('FLEURY', 'EINSTEIN', 'HILAB', 'HPARDINI'):
        return ['arbo', 'respat']
    
    if lab == 'SABIN':
        if 'arbo' in filename.lower():
            return ['arbo']
        return ['respat']

    if lab == 'HLAGYN':
        if 'arbo' in filename.lower():
            return ['arbo']
        return ['respat']

    return []

if __name__ == "__main__":
    API_ENPOINT = os.getenv("MANAGER_ENDPOINT")
    APP_NAME    = 'GMail'

    EMAIL_ADDRESS         = os.getenv("EMAIL_ADDRESS")
    EMAIL_APP_PASSWORD    = os.getenv("EMAIL_APP_PASSWORD")
    EMAIL_QUERY_SENDER    = "joaopedrodasilvalima@gmail.com"
    EMAIL_QUERY_PAST_DAYS = 30

    IMAP_SERVER = 'imap.gmail.com'
    current_date = datetime.now().strftime("%Y-%m-%d")

    if API_ENPOINT is None:
        print(f"ERROR! API_ENPOINT is None")
        exit(1)

    # ===================================
    # Logger configuration
    # ===================================
    manager_interface = ManagerInterface(APP_NAME, API_ENPOINT)
    logger = manager_interface.logger

    # Connect to the IMAP server
    logger.info(f"Connecting to the IMAP server using '{EMAIL_ADDRESS}'")
    
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL_ADDRESS, EMAIL_APP_PASSWORD)
    mail.select('inbox')  # Você pode escolher outra pasta

    query_start_date = last_download_time().strftime('%d-%b-%Y')
    logger.info(f"Searching emails from {query_start_date} up to NOW.")

    logger.info(f"Loading list of e-mail senders from 'emails.json'")
    lab_sender_email_list = load_emails_list()
    if not lab_sender_email_list:
        logger.critical(f"Unable to read file 'emails.json'")
        exit(1)
    
    logger.info(f"Searching for e-mails sent by the following labs: {','.join(lab_sender_email_list.keys())}")
    for lab_name, lab_sender_list in lab_sender_email_list.items():
        
        query_sender_part = " ".join([f'FROM "{email_sender}"' for email_sender in lab_sender_list])
        query_string = f'SINCE {query_start_date} ({query_sender_part})'
        logger.info(f"Searching e-mails for lab {lab_name}. Query string: {query_string}")
        
        result, data = mail.search(None, query_string)
        email_ids = data[0].split()

        if not email_ids:
            logger.info("No e-mails found.")
            continue

        logger.info(f"Found {len(email_ids)} e-mails.")

        for email_id in email_ids:
            # Get e-mail attachments
            attachments = get_attachments_from_email(mail, email_id)
            if not attachments:
                logger.info(f"No attachments found for email ID {email_id}.")
                continue
            
            for filename, file_bytes in attachments:
                logger.info(f"Found file {filename}. ")
                projects = determine_project_from_file_name(lab_name, filename)

                if not projects:
                    logger.error(f"Unable to determine which project (arbo/respat) the file '{filename}' from {lab_name} is part of. The file will not be uploaded.")
                    continue

                for project in projects:

                    logger.info(f"Uploading file {filename} (project={project})...")
                    new_filename = f"{lab_name}_{current_date}__{filename}"

                    manager_interface.upload_file(
                        organization=lab_name.lower(),
                        project=project,
                        file_content=file_bytes,
                        file_name=new_filename
                    )
                    logger.info(f"Finished uploading file {filename}!")
    
    update_last_download_time()
    logger.info(f"Finished extracting all data. Last execution date set to {current_date}")
    manager_interface.close_session()

    mail.close()
    logger.info("Finished pipeline.")
