import unittest
import requests
from http import HTTPStatus
from datetime import datetime

class TestAPIStatusRoute(unittest.TestCase):
    
    def setUp(self) -> None:
        self.api_base_url = "http://localhost:8000"
        self.log_endpoint = f"{self.api_base_url}/log"
        self.status_endpoint = f"{self.api_base_url}/status"
        self.app_name = "TestAPIStatusRoute"  # App Name

        # Create a valid session_id
        response = requests.get(self.log_endpoint, params={"app_name": self.app_name})
        if response.status_code == HTTPStatus.CREATED:
            self.session_id = response.json().get("session_id")
        else:
            self.fail("Falha ao obter session_id no setup. Status do GET inesperado.")

    # TESTS /status
    def test_PUT_status_200_OK_update_existing_status(self):
        new_status = {
            "session_id": self.session_id,
            "status": "COMPLETED"  # New Session STATUS
        }

        response = requests.put(self.status_endpoint, json=new_status)
        print(response.json())
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.json()["status"], "COMPLETED")

    def test_PUT_status_200_OK_update_existing_status_and_timestamp(self):
        new_status = {
            "session_id": self.session_id,
            "status": "COMPLETED",  # New Session STATUS
            "end": datetime.now().isoformat()
        }

        response = requests.put(self.status_endpoint, json=new_status)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.json()["status"], "COMPLETED")

    def test_PUT_status_404_not_found(self):
        session_id = "nonexistent_session"  # Use um session_id que não existe
        new_status = {
            "session_id": session_id,
            "status": "COMPLETED"
        }

        response = requests.put(self.status_endpoint, json=new_status)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertIn("Session ID not found", response.json()["detail"])

    def test_PUT_status_missing_parameters(self):
        response = requests.put(self.status_endpoint, json={})
        self.assertEqual(response.status_code, HTTPStatus.UNPROCESSABLE_ENTITY)


if __name__ == "__main__":
    unittest.main()