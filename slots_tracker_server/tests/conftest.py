import datetime

import pytest

from slots_tracker_server import app as flask_app
from slots_tracker_server.models import Expense, PayMethods, Categories, Withdrawal, Kinds


@pytest.fixture(scope="session", autouse=True)
def client():
    flask_client = flask_app.test_client()
    # Clean the DB
    Expense.objects.delete()
    PayMethods.objects.delete()
    Categories.objects.delete()
    Withdrawal.objects.delete()
    Kinds.objects.delete()

    # create fake documents
    pay_method = PayMethods(name='Visa').save()
    PayMethods(name='Visa1111').save()
    PayMethods(name='Visa2222').save()
    PayMethods(name='Visa3333').save()
    category = Categories('Cat 1').save()
    Categories('Cat 11').save()
    Categories('Cat 111').save()
    Categories('Cat 1111').save()
    Categories('Cat 11111').save()
    kind = Kinds('Kind 1').save()
    Kinds('Kind 2').save()
    Kinds('Kind 3').save()

    now_date = datetime.datetime.utcnow
    expense_data = dict(amount=200, description='Random stuff', pay_method=pay_method.id, timestamp=now_date,
                        category=category.id)
    Expense(**expense_data).save()

    withdrawal_data = dict(amount=200, pay_method=pay_method.id, timestamp=now_date, kind=kind.id)
    Withdrawal(**withdrawal_data).save()
    # Create deleted items
    expense_data['active'] = False
    Expense(**expense_data).save()
    withdrawal_data['active'] = False
    Withdrawal(**withdrawal_data).save()

    yield flask_client

    # Clean the DB
    Expense.objects.delete()
    PayMethods.objects.delete()
    Categories.objects.delete()
    Withdrawal.objects.delete()
    Kinds.objects.delete()
