from datetime import datetime

import pytest

from slots_tracker_server import app as flask_app
from slots_tracker_server.models import Expense, PayMethods, Categories

AMOUNT_1 = 200
AMOUNT_2 = 500
AMOUNT_3 = 400
EXPENSES_WITH_AMOUNT_3 = 3


@pytest.fixture(scope="function", autouse=True)
def client():
    flask_client = flask_app.test_client()
    # Clean the DB
    Expense.objects.delete()
    PayMethods.objects.delete()
    Categories.objects.delete()

    # create fake documents
    pay_method = PayMethods(name='Visa').save()
    pay2 = PayMethods(name='Visa1111').save()
    PayMethods(name='Visa2222').save()
    PayMethods(name='Visa3333').save()

    PayMethods(name='Parser 1234').save()
    # Colu
    PayMethods(name='Colu - Xxxxxx').save()

    category = Categories(name='Cat 1').save()
    cat2 = Categories(name='Cat 11').save()
    Categories(name='Cat 111').save()
    Categories(name='Cat 1111').save()
    Categories(name='Cat 11111').save()
    Categories(name='Eating out').save()

    now_date = datetime.utcnow
    expense_data = dict(amount=AMOUNT_1, pay_method=pay_method.id, timestamp=now_date, category=category.id)
    Expense(**expense_data).save()

    Expense(amount=AMOUNT_2, pay_method=pay2, category=cat2, timestamp=now_date).save()
    for _ in range(EXPENSES_WITH_AMOUNT_3):
        Expense(amount=AMOUNT_3, pay_method=pay_method, category=category, timestamp=now_date).save()

    # Create deleted items
    expense_data['active'] = False
    Expense(**expense_data).save()

    yield flask_client

    # Clean the DB
    Expense.objects.delete()
    PayMethods.objects.delete()
    Categories.objects.delete()
