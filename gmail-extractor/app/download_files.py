import os
import json
import logging
import datetime
import base64
import io

from tests import test_if_token_is_still_active, test_token_exists

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from typing import List, Tuple, Optional, Dict, Any

# Configuração do logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# If modifying these scopes, delete the file token.json.

# [WIP] Tudo isso vai virar variável de ambiente
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
TOKEN_PATH = 'token.json'

class EmailFileDownloader:
    """
    Class used to download the data sent by email by the labs.

    Uses Google API to authenticate and get access to the inbox.
    """

    def __init__(self) -> None:
        self.email_list_file = 'emails.json'  # JSON file containing a list of each lab's emails
        self.token_path = 'token.json'  # JSON file containing the authorization token to the Google API
        self.scopes = ["https://www.googleapis.com/auth/gmail.readonly"]
        self.last_download_time_file = 'last_download_time.txt'

        self.logger = logging.getLogger("FILE DOWNLOADER")

    def run(self) -> None:
        """
        Main method to run the email file downloader process.
        """
        email_list = self.load_email_list_from_file()
        gmail_service = self.get_google_api_service()
        self.download_attachments_from_email(email_list, gmail_service)
        self.write_last_email_download_time()

    def load_email_list_from_file(self) -> Optional[Dict[str, List[str]]]:
        """
        Loads the email list from the specified JSON file.

        Returns:
            dict: A dictionary with lab names as keys and lists of emails as values.
        """
        if not os.path.exists(self.email_list_file):
            self.logger.error(f"Unable to load file {self.email_list_file}.")
            return None

        with open(self.email_list_file, 'r') as arquivo:
            email_list = json.load(arquivo)

        self.logger.info(f"Successfully loaded {self.email_list_file}")
        return email_list

    def get_google_api_service(self) -> Optional[Any]:
        """
        Authenticates with the Google API and returns the Gmail service object.

        Returns:
            googleapiclient.discovery.Resource: The Gmail service object.
        """
        creds = Credentials.from_authorized_user_file(self.token_path, self.scopes)
        try:
            service = build('gmail', 'v1', credentials=creds)
        except HttpError as error:
            self.logger.error(f"An error occurred: {error}")
            return None

        self.logger.info("Successfully authenticated in the Google API")
        return service

    def download_attachments_from_email(self, email_list: Dict[str, List[str]], gmail_service: Any) -> None:
        """
        Downloads attachments from emails based on the given email list and Gmail service.

        Args:
            email_list (dict): A dictionary with lab names as keys and lists of emails as values.
            gmail_service (googleapiclient.discovery.Resource): The Gmail service object.
        """
        labs = list(email_list.keys())
        self.logger.info(f"Downloading files from the following labs: {', '.join(labs)}")

        current_date = self.get_last_email_download_time()
        past_date = current_date - datetime.timedelta(days=1)
        past_date_str = past_date.strftime('%Y/%m/%d')

        self.logger.info(f"Considering only emails after {past_date.strftime('%Y-%m-%d')}")

        for lab, emails in email_list.items():
            self.logger.info(f"Downloading files for {lab}")
            lab_data_path = f'./../data/{lab}'

            if not os.path.exists(lab_data_path):
                self.logger.warning(f"Unable to locate path {lab_data_path}. This is the path where the data would be saved. Skipping lab {lab}.")

            for email in emails:
                email_query = f"from:{email} after:{past_date_str} has:attachment"
                lab_attachment_buffers = self.download_attachments_from_lab(email_query, gmail_service)
                self.save_attachments_in_folder(lab_attachment_buffers, lab, lab_data_path)

    def download_attachments_from_lab(self, email_query: str, gmail_service: Any) -> List[Tuple[str, io.BytesIO, str, str]]:
        """
        Downloads attachments from the lab emails based on the given query.

        Args:
            email_query (str): The query to search for emails.
            gmail_service (googleapiclient.discovery.Resource): The Gmail service object.

        Returns:
            list: A list of tuples containing the filename, buffer, date, and sender of each attachment.
        """
        attachment_buffers = []

        results = gmail_service.users().messages().list(userId='me', q=email_query).execute()
        messages = results.get('messages', [])

        if not messages:
            self.logger.info(f"No messages found for query {email_query}")
            return attachment_buffers

        for message in messages:
            msg = gmail_service.users().messages().get(userId='me', id=message['id']).execute()

            headers = msg['payload'].get('headers', [])
            date = next(header['value'] for header in headers if header['name'] == 'Date')
            sender = next(header['value'] for header in headers if header['name'] == 'From')
            parts = msg['payload'].get('parts', [])

            for part in parts:
                if part['filename']:
                    self.logger.info(f"Found an attachment: {part['filename']}")
                    attachment_id = part['body']['attachmentId']
                    attachment = gmail_service.users().messages().attachments().get(
                        userId='me', messageId=message['id'], id=attachment_id
                    ).execute()

                    data = base64.urlsafe_b64decode(attachment['data'].encode('UTF-8'))
                    buffer = io.BytesIO(data)
                    attachment_buffers.append((part['filename'], buffer, date, sender))

        return attachment_buffers

    def save_attachments_in_folder(self, attachments: List[Tuple[str, io.BytesIO, str, str]], lab_name: str, path: str) -> None:
        """
        Saves the downloaded attachments to the specified folder.

        Args:
            attachments (list): A list of tuples containing the filename, buffer, date, and sender of each attachment.
            lab_name (str): The name of the lab.
            path (str): The path to save the attachments.
        """
        if not os.path.exists(path):
            self.logger.error(f"Unable to save files from `{lab_name}` into folder - {path} does not exist")
            return

        for filename, buffer, date, sender in attachments:
            date_str = datetime.datetime.strptime(date, '%a, %d %b %Y %H:%M:%S %z').strftime('%Y-%m-%d')
            new_filename = f"{lab_name}_{date_str}__{filename}"
            file_path = os.path.join(path, new_filename)
            with open(file_path, 'wb') as f:
                f.write(buffer.getvalue())

            self.logger.info(f"Saved attachment {filename} as {new_filename}")

    def get_last_email_download_time(self) -> datetime.datetime:
        """
        Gets the last email download time from the specified file.

        Returns:
            datetime.datetime: The datetime object representing the last email download time.
        """
        TIME_FORMAT = "%Y-%m-%d"

        if not os.path.exists(self.last_download_time_file):
            self.write_last_email_download_time()

        with open(self.last_download_time_file, 'r') as f:
            last_email_download_time = datetime.datetime.strptime(f.read(), TIME_FORMAT)

        return last_email_download_time

    def write_last_email_download_time(self) -> None:
        """
        Writes the current date and time to the specified file as the last email download time.
        """
        TIME_FORMAT = "%Y-%m-%d"

        current_date = datetime.datetime.now()
        with open(self.last_download_time_file, 'w') as f:
            f.write(current_date.strftime(TIME_FORMAT))


if __name__ == "__main__":
    
    if not test_token_exists(TOKEN_PATH):
        exit()

    if not test_if_token_is_still_active(TOKEN_PATH, SCOPES):
        exit()

    email_file_downloader = EmailFileDownloader()
    email_file_downloader.run()
