# from emplify_report_exporter import EmplifyReportExporter
import email
import imaplib
import re
import requests
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta

#### Load environment variables
load_dotenv()
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_APP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")
EMAIL_QUERY_SENDER = "joaopedrodasilvalima@gmail.com"
EMAIL_QUERY_PAST_DAYS = 180

IMAP_SERVER = 'imap.gmail.com'

#### Connect to the IMAP server
mail = imaplib.IMAP4_SSL(IMAP_SERVER)
mail.login(EMAIL_ADDRESS, EMAIL_APP_PASSWORD)
mail.select('inbox')  # Você pode escolher outra pasta

#### Query for unread messages from a Emplify, newer than 1 day
date_threshold = (datetime.now() - timedelta(days=EMAIL_QUERY_PAST_DAYS)).strftime('%d-%b-%Y')
date_threshold = f'"{date_threshold}"'
query_string = f'SINCE {date_threshold} FROM "{EMAIL_QUERY_SENDER}"'
result, data = mail.search(None, query_string)
email_ids = data[0].split()
print(f"Found {len(email_ids)} unread messages from ")

if not email_ids or len(email_ids) == 0:
    print("No messages found")
    exit()

#### Export the excel reports
for email_id in email_ids:
    # Fetch the email
    result, data = mail.fetch(email_id, '(RFC822)')
    raw_email = data[0][1]
    email_message = email.message_from_bytes(raw_email)
    print(f"Processing message from {email_message['date']} with subject: {email_message['subject']}")

    # Get the body of the email and extract the URL
    if email_message.is_multipart():
        for part in email_message.walk():
            if part.get_content_type() == "text/plain":
                body = part.get_payload(decode=True).decode(part.get_content_charset())
    else:
        body = email_message.get_payload(decode=True).decode(email_message.get_content_charset())



mail.close()

print("All reports exported successfully")

