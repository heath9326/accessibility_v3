import unittest
from unittest import TestCase

from fastapi.testclient import TestClient

import crud
from database import Base
from main import app  # replace with the actual import path of your FastAPI app

from unittest.mock import patch
import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class TestCreateInitialText(TestCase):

    def setUp(self):
        # Create an in-memory SQLite database
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)  # Create tables
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()
        self.client = TestClient(app)

    def tearDown(self):
        self.session.close()
        self.engine.dispose()

    def test_create_initial_text(self):
        # Prepare the data for the test
        initial_text = "Sample initial text for testing."

        # Mocking the database operations for testing

        # mock_create.return_value = models.InitialText(id=1, text=initial_text)  # mock the return value

        # Sending a POST request to the endpoint
        response = self.client.post("/assessment", data={"initial_text": initial_text})

        # Ensure the response status code is 200 (OK)
        assert response.status_code == 200

        # Ensure the response contains the expected data
        response_data = response.json()

        # Example: Assert if the returned data includes the expected ID and some other properties.
        assert "id" in response_data
        assert response_data["id"] == 1  # Mocked ID

        # Additional assertions can be done based on the expected structure of the response


if __name__ == "__main__":
    unittest.main()
