import datetime

import pytest

from slots_tracker_server import app as flask_app
from slots_tracker_server.expense import Expense, PayMethods


@pytest.fixture(scope="session", autouse=True)
def client():
    flask_client = flask_app.test_client()
    # Clean the DB
    Expense.objects.delete()
    PayMethods.objects.delete()

    # create fake PayMethods
    PayMethods('Visa').save()
    # Create fake Expense
    Expense(amount=200, description='Random stuff', pay_method=PayMethods.objects().first(),
            timestamp=datetime.datetime.utcnow).save()

    yield flask_client

    # Clean the DB
    Expense.objects.delete()
    PayMethods.objects.delete()
