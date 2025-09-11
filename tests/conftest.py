import pytest
import sys
import os

# Make sure the parent directory is in sys.path so "api" can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from api.index import app as flask_app   # <-- updated import

@pytest.fixture(scope="session")
def client():
    flask_app.config.update(TESTING=True)
    return flask_app.test_client()