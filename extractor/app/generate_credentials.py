# ========================================= #
# RODE ESSE SCRIPT PARA GERAR UM NOVO TOKEN #
# ========================================= #

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow


# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
TOKEN_FILE       = "token.json"
CREDENTIALS_FILE = "credentials.json"

def generate_credentials():
	"""
		Generate a new authorization token to download e-mail files. 
	"""
	creds = None
	# The file token.json stores the user's access and refresh tokens, and is
	# created automatically when the authorization flow completes for the first
	# time.
	if os.path.exists(TOKEN_FILE):
		creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

	# If there are no (valid) credentials available, let the user log in.
	if not creds or not creds.valid:
		if creds and creds.expired and creds.refresh_token:
			creds.refresh(Request())
		else:
			flow = InstalledAppFlow.from_client_secrets_file(
			CREDENTIALS_FILE, SCOPES
			)
			creds = flow.run_local_server(port=0)
	# Save the credentials for the next run
	with open(TOKEN_FILE, "w") as token:
		token.write(creds.to_json())

if __name__ == "__main__":
	generate_credentials()