import pytest
import sys
import os

# Ensure repo root is importable so we can import api.index
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from api.index import app as flask_app

@pytest.fixture(scope="session")
def client():
    flask_app.config.update(TESTING=True)
    return flask_app.test_client()