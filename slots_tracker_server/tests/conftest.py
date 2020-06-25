from datetime import datetime

import pytest

from slots_tracker_server import app as flask_app
from slots_tracker_server.models import Expense, PayMethods, Categories


@pytest.fixture(scope="function", autouse=True)
def client():
    flask_client = flask_app.test_client()
    # Clean the DB
    Expense.objects.delete()
    PayMethods.objects.delete()
    Categories.objects.delete()

    # create fake documents
    pay_method = PayMethods(name='Visa').save()
    PayMethods(name='Visa1111').save()
    PayMethods(name='Visa2222').save()
    PayMethods(name='Visa3333').save()

    PayMethods(name='Parser 1234').save()

    category = Categories(name='Cat 1').save()
    Categories(name='Cat 11').save()
    Categories(name='Cat 111').save()
    Categories(name='Cat 1111').save()
    Categories(name='Cat 11111').save()

    now_date = datetime.utcnow
    expense_data = dict(amount=200, pay_method=pay_method.id, timestamp=now_date, category=category.id)
    Expense(**expense_data).save()

    # Create deleted items
    expense_data['active'] = False
    Expense(**expense_data).save()

    yield flask_client

    # Clean the DB
    Expense.objects.delete()
    PayMethods.objects.delete()
    Categories.objects.delete()
