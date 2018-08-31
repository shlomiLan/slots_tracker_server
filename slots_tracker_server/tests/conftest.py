import datetime

import pytest

from slots_tracker_server import app as flask_app
from slots_tracker_server.models import Expense, PayMethods, Categories


@pytest.fixture(scope="session", autouse=True)
def client():
    flask_client = flask_app.test_client()
    # Clean the DB
    Expense.objects.delete()
    PayMethods.objects.delete()
    Categories.objects.delete()

    # create fake PayMethods
    pay_method = PayMethods(name='Visa').save()

    category = Categories('Cat 1').save()

    # Create fake Expense
    now_date = datetime.datetime.utcnow
    expense_data = dict(amount=200, description='Random stuff', pay_method=pay_method.id, timestamp=now_date,
                        category=category.id)  # noqa
    Expense(**expense_data).save()
    # Create deleted item to tests the are not returned
    expense_data['active'] = False
    Expense(**expense_data).save()

    yield flask_client

    # Clean the DB
    Expense.objects.delete()
    PayMethods.objects.delete()
    Categories.objects.delete()
