# APIClient fixture to be used in tests
import pytest
from rest_framework.test import APIClient

@pytest.fixture(scope="class")
def api_client():
    """Fixture to provide an API client"""
    yield APIClient()
