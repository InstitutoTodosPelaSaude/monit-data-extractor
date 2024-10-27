import unittest
import requests
from http import HTTPStatus

class TestAPIHosts(unittest.TestCase):

    def setUp(self) -> None:
        self.api_base_url = "http://localhost:8000"
        self.log_endpoint = f"{self.api_base_url}/log"
        self.app_name = "TestApp"  # App Name

        # Create a valid session_id
        response = requests.get(self.log_endpoint, params={"app_name": self.app_name})
        if response.status_code == HTTPStatus.CREATED:
            self.session_id = response.json().get("session_id")
        else:
            self.fail("Falha ao obter session_id no setup. Status do GET inesperado.")

    # GET method without parameters returns 201 OK and JSON formatted as {"session_id": session_id}
    def test_GET_log_201_OK__fetch_log(self):
        response = requests.get(self.log_endpoint, params={"app_name": self.app_name})
        self.assertEqual(response.status_code, HTTPStatus.CREATED)
        self.assertIn("session_id", response.json())

    # POST method with correct parameters returns 200 OK
    def test_POST_log_200_OK__create_log(self):
        payload = {
            "session_id": self.session_id,  # Session 
            "app_name": self.app_name,
            "type": "INFO",
            "message": "Test message"
        }
        response = requests.post(self.log_endpoint, json=payload)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn("session_id", response.json())

    # POST method with wrong 'type' value returns error
    def test_POST_log_422_UnprocessableEntity__wrong_type(self):
        payload = {
            "session_id": self.session_id,
            "app_name": self.app_name,
            "type": "INVALID_TYPE",
            "message": "Test message"
        }
        response = requests.post(self.log_endpoint, json=payload)
        self.assertEqual(response.status_code, HTTPStatus.UNPROCESSABLE_ENTITY)
        self.assertIn("detail", response.json())

    # POST method with invalid session_id returns 404 error
    def test_POST_log_404_NotFound__invalid_session_id(self):
        payload = {
            "session_id": "nonexistent_session",
            "app_name": self.app_name,
            "type": "INFO",
            "message": "Test message"
        }
        response = requests.post(self.log_endpoint, json=payload)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertIn("detail", response.json())

    # POST method with missing parameters returns BAD REQUEST
    def test_POST_log_422_BadRequest__missing_parameters(self):
        payload = {
            "session_id": self.session_id,
            "app_name": self.app_name
        }
        response = requests.post(self.log_endpoint, json=payload)
        self.assertEqual(response.status_code, HTTPStatus.UNPROCESSABLE_ENTITY)
        self.assertIn("detail", response.json())

if __name__ == "__main__":
    unittest.main()
