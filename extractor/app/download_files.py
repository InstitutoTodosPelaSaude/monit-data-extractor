import os
import base64
import datetime
import io
import logging
import json

from tests import test_if_token_is_still_active, test_token_exists

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Configuração do logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# If modifying these scopes, delete the file token.json.

# [WIP] Tudo isso vai virar variável de ambiente
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
TOKEN_PATH = 'token.json'
lab_emails = ""

class EmailFileDownloader:

    def __init__(self) -> None:
        self.email_list_file = 'emails.json' # json file containing a list of each labs' emails
        self.logger = logging.getLogger("FILE DOWNLOADER")


    def run(self) -> None:
        email_list = self.load_email_list_from_file()


    def load_email_list_from_file(self):

        if not os.path.exists(self.email_list_file):
            self.logger.error(f"Unable to load file {self.email_list_file}.")
            return None
        
        with open(self.email_list_file, 'r') as arquivo:
            email_list = json.load(arquivo)

        self.logger.info(f"Successfully loaded {self.email_list_file}")

        return email_list


def download_attachments_from_email(email_query):
    creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    attachment_buffers = []
    try:
        # Call the Gmail API
        service = build('gmail', 'v1', credentials=creds)
        results = service.users().messages().list(userId='me', q=email_query).execute()
        messages = results.get('messages', [])

        if not messages:
            logger.info(f"No messages found for query {email_query}")
            return attachment_buffers

        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id']).execute()
            headers = msg['payload'].get('headers', [])
            date = next(header['value'] for header in headers if header['name'] == 'Date')
            sender = next(header['value'] for header in headers if header['name'] == 'From')
            parts = msg['payload'].get('parts', [])
            for part in parts:
                if part['filename']:
                    logger.info(f"Found an attachment: {part['filename']}")
                    attachment_id = part['body']['attachmentId']
                    attachment = service.users().messages().attachments().get(
                        userId='me', messageId=message['id'], id=attachment_id
                    ).execute()

                    data = base64.urlsafe_b64decode(attachment['data'].encode('UTF-8'))
                    buffer = io.BytesIO(data)
                    attachment_buffers.append((part['filename'], buffer, date, sender))

    except HttpError as error:
        logger.error(f"An error occurred: {error}")

    return attachment_buffers

def save_attachments_in_folder(attachments, lab_name, path):
    # Create the directory if it doesn't exist
    if not os.path.exists(path):
        logger.error( f"Unable to salve files from `{lab_name}` into folder - {path} does not exist" )
        return

    for filename, buffer, date, sender in attachments:
        # Format date to be used in the filename
        # Date Format in GMAIL -> YYYY-MM-DD
        date_str = datetime.datetime.strptime(date, '%a, %d %b %Y %H:%M:%S %z').strftime('%Y-%m-%d')
        # Create the new filename
        new_filename = f"{lab_name}_{date_str}__{filename}"
        # Define the path to save the file
        file_path = os.path.join(path, new_filename)
        # Save the file
        with open(file_path, 'wb') as f:
            f.write(buffer.getvalue())

        logger.info(f"Saved attachment {filename} as {new_filename}")

def download_files_from_labs(lab_emails):
    # Get the current date and calculate the date 30 days ago
    current_date = datetime.datetime.now()
    past_date = current_date - datetime.timedelta(days=30)
    past_date_str = past_date.strftime('%Y/%m/%d')

    for lab, emails in lab_emails.items():
        logger.info(f"BUSCANDO DADOS DE {lab}")
        for email in emails:
            email_query = f"from:{email} after:{past_date_str} has:attachment"
            attachments = download_attachments_from_email(email_query)

            if len(attachments) <= 0:
                continue

            save_attachments_in_folder(attachments, lab, f'/data/{lab}')            

if __name__ == "__main__":
    
    if not test_token_exists(TOKEN_PATH):
        exit()

    if not test_if_token_is_still_active(TOKEN_PATH, SCOPES):
        exit()

    # download_files_from_labs(lab_emails)

    email_file_downloader = EmailFileDownloader()
    email_file_downloader.run()
