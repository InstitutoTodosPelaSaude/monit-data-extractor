import logging
import requests
from io import BytesIO
from datetime import datetime

logging.basicConfig(
    level=logging.DEBUG,  # Set the minimum logging level
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Log message format
)

class JSONFormatter(logging.Formatter):
    def format(self, record):
        # Create a dictionary representation of the log record
        log_record = {
            'timestamp': self.formatTime(record),
            'level': record.levelname,
            'message': record.getMessage(),
        }
        return log_record

class APILogHandler(logging.Handler):
    def __init__(self, endpoint, session_id, app_name):
        """Wrapper class to automatically send the logs to the Monitor API

        Args:
            endpoint (str): API Endpoint
            session_id (str): Logs session. Retrieved from the API.
            app_name (str): Name of the app that generate the logs
        """
        super().__init__()
        self.endpoint = endpoint
        self.session_id = session_id
        self.app_name   = app_name

    def emit(self, record):
        # Create a log message
        log_entry = self.format(record)
        # Send the log message to the specified API endpoint
        log_entry['session_id'] = self.session_id
        log_entry['app_name']   = self.app_name

        try:
            response = requests.post(f"{self.endpoint}/log", json=log_entry)
            response.raise_for_status()  # Raise an error for bad responses
        except Exception as e:
            print(f"Failed to send log to API: {e}")

class ManagerInterface():

    def __init__(self, app_name: str, endpoint: str) -> None:
        self.app_name = app_name
        self.endpoint = endpoint
        self.logger = logging.getLogger(app_name)
        self.session_id = None
        self.configure_api_logs_handler()

    def configure_api_logs_handler(self):
        self.logger.info("Configuring API Logs handler.")
        
        try:
            response = requests.get(f"{self.endpoint}/log", params={'app_name': self.app_name})
            response.raise_for_status()
        except Exception as e:
            self.logger.error(f"Unable to retrieve a Logs' Session ID from the API. {e}")

        self.session_id = response.json()['session_id']
        self.logger.info(f"Session id: '{self.session_id}'")

        api_handler = APILogHandler(self.endpoint, session_id=self.session_id, app_name=self.app_name)
        json_formatter = JSONFormatter()
        api_handler.setFormatter(json_formatter)
        self.logger.addHandler(api_handler)

    def upload_file(
            self, 
            organization: str, 
            project: str, 
            file_content: BytesIO,
            file_name: str
        ):

        response = requests.post(
            f"{self.endpoint}/file", 
            params={
                "session_id": self.session_id,
                "organization": organization,
                "project": project
            }, 
            files={
                "file": (file_name, file_content, 'text/csv')
            }
        )

    def close_session(self, status="COMPLETED"):
        response = requests.put(
            f"{self.endpoint}/status", 
            json = {
                "session_id": self.session_id,
                "status": status,  # New Session STATUS
                "end": datetime.now().isoformat()
            }
        )
