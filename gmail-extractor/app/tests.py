
import os
import base64
import datetime
import io
import logging

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Configuração do logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_token_exists(path):
    if os.path.exists(path):
        logger.info("O Arquivo de TOKEN existe")
        return True
    return False

def test_if_token_is_still_active(path, scopes):
    creds = Credentials.from_authorized_user_file(path, scopes)
    # If there are no (valid) credentials available
    if not creds or not creds.valid:
        logger.error("Token não existe ou não é mais válido. Favor gerar novo TOKEN.")
        return False
    if not refresh_token(creds):
        return False
    return True

def refresh_token(creds):
    if creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            with open("token.json", "w") as token:
                token.write(creds.to_json())
            logger.info("Token renovado com sucesso.")
        except Exception as e:
            logger.error(f"Erro ao renovar o token: {e}")
            return False
    return True