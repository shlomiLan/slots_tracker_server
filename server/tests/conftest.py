import pytest

from server import app as flask_app
from server.expense import Expense


@pytest.fixture
def client():
    client = flask_app.test_client()
    # Clean the DB
    Expense.objects.delete()
    yield client
