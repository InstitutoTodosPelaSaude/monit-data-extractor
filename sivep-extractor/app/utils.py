import logging
import requests

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