import pytest

from server import app as flask_app
from server.expense import Expense, PayMethods


@pytest.fixture
def client():
    client = flask_app.test_client()
    # Clean the DB
    Expense.objects.delete()
    PayMethods.objects.delete()

    # create fake PayMethods
    PayMethods('Visa').save()
    yield client
