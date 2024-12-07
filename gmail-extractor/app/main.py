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

def last_download_time():
    try:
        with open('/app/last_download_time.txt', 'r') as f:
            return datetime.strptime(f.read(), '%Y-%m-%d')
    except Exception as e:
        return (datetime.now() - timedelta(days=30))
    
def load_emails_list():
    try:
        with open('/app/emails.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        return None

if __name__ == "__main__":
    API_ENPOINT = os.getenv("MANAGER_ENDPOINT")
    APP_NAME    = 'GMail'

    EMAIL_ADDRESS         = os.getenv("EMAIL_ADDRESS")
    EMAIL_APP_PASSWORD    = os.getenv("EMAIL_APP_PASSWORD")
    EMAIL_QUERY_SENDER    = "joaopedrodasilvalima@gmail.com"
    EMAIL_QUERY_PAST_DAYS = 30

    IMAP_SERVER = 'imap.gmail.com'

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


    mail.close()
