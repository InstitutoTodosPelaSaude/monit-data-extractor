import unittest
import requests
from http import HTTPStatus

class TestAPIFileRoute(unittest.TestCase):
    
    def setUp(self) -> None:
        self.api_base_url = "http://localhost:8000"
        self.file_endpoint = f"{self.api_base_url}/file"
        self.log_endpoint = f"{self.api_base_url}/log"
        self.app_name = "TestAPIFileRoute"
        
        # Cria um session_id válido
        response = requests.get(self.log_endpoint, params={"app_name": self.app_name})
        if response.status_code == HTTPStatus.CREATED:
            self.session_id = response.json().get("session_id")
        else:
            self.fail("Falha ao obter session_id no setup. Status do GET inesperado.")

        with open("testfile.txt", "w") as f:
            f.write("This is a test file content.")
        with open("testfile.exe", "w") as f:
            f.write("This is a test .exe file content.")

    def test_POST_file_200_OK_successful_upload(self):

        file_data = {
            "session_id": self.session_id,
            "organization": "TestOrg",
            "project": "TestProject"
        }

        with open("testfile.txt", "rb") as file:
            files = {"file": file}
            response = requests.post(self.file_endpoint, params=file_data, files=files)
        
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.json()["session_id"], self.session_id)
        self.assertEqual(response.json()["organization"], "TestOrg")
        self.assertEqual(response.json()["project"], "TestProject")
        self.assertIn("filename", response.json())

    def test_POST_file_422_missing_required_field(self):
        file_data = {
            "organization": "TestOrg",
            "project": "TestProject"
        }

        with open("testfile.txt", "rb") as file:
            files = {"file": file}
            response = requests.post(self.file_endpoint, params=file_data, files=files)
        
        self.assertEqual(response.status_code, HTTPStatus.UNPROCESSABLE_ENTITY)
        print(response.json())
        self.assertIn("detail", response.json())

    def test_POST_file_404_invalid_session_id(self):
        file_data = {
            "session_id": "nonexistent_session",
            "organization": "TestOrg",
            "project": "TestProject"
        }

        with open("testfile.txt", "rb") as file:
            files = {"file": file}
            response = requests.post(self.file_endpoint, params=file_data, files=files)
        
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertIn("Session ID not found", response.json()["detail"])

    def test_POST_file_400_invalid_file_format(self):
        file_data = {
            "session_id": self.session_id,
            "organization": "TestOrg",
            "project": "TestProject"
        }

        with open("testfile.exe", "rb") as file:
            files = {"file": file}
            response = requests.post(self.file_endpoint, params=file_data, files=files)
        
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        self.assertIn("Invalid file format", response.json()["detail"])

    def test_POST_file_422_missing_file(self):
        """Testa o upload sem incluir um arquivo no request."""
        file_data = {
            "session_id": self.session_id,
            "organization": "TestOrg",
            "project": "TestProject"
        }

        response = requests.post(self.file_endpoint, params=file_data)
        
        self.assertEqual(response.status_code, HTTPStatus.UNPROCESSABLE_ENTITY)

if __name__ == "__main__":
    unittest.main()
