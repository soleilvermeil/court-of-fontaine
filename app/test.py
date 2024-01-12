import subprocess
import requests
import time
import json
import unittest

TARGET_DOMAIN = "http://127.0.0.1:8000"
TIME_TO_WAIT = 5

class DjangoServerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Start the Django development server in a separate process
        cls.server_process = subprocess.Popen(["python", "manage.py", "runserver"])
        # Wait for the server to start (adjust the time based on your project)
        time.sleep(5)

    @classmethod
    def tearDownClass(cls):
        # Stop the Django development server process
        if cls.server_process.poll() is None:
            cls.server_process.terminate()
            cls.server_process.wait()

    def test_server_access(self):
        url = TARGET_DOMAIN
        response = requests.get(url)
        self.response = response
        self.assertEqual(response.status_code, 200, "Failed to access the website")

    def test_player_access(self):
        url = f"{TARGET_DOMAIN}/uid/703047530"
        response = requests.get(url)
        self.response = response
        self.assertEqual(response.status_code, 200, "Failed to access a player's page")

    def test_player_api(self):
        url = f"{TARGET_DOMAIN}/api/703047530"
        response = requests.get(url)
        json_data = response.json() if response.status_code == 200 else {}
        self.assertIn("uid", json_data, "'uid' field not found in the JSON response")

    def test_character_access(self):
        url = f"{TARGET_DOMAIN}/char/furina"
        response = requests.get(url)
        self.response = response
        self.assertEqual(response.status_code, 200, "Failed to access a character's page")

    def test_character_api(self):
        url = f"{TARGET_DOMAIN}/api/furina"
        response = requests.get(url)
        json_data = response.json() if response.status_code == 200 else {}
        self.assertIn("name", json_data, "'name' field not found in the JSON response")

if __name__ == "__main__":
    unittest.main()
