import json

import pytest
from mongoengine.errors import FieldDoesNotExist

from slots_tracker_server.expense import Expense, PayMethods


def test_field_does_not_exist():
    with pytest.raises(FieldDoesNotExist):
        Expense(amounta=200, description='Random stuff', pay_method=PayMethods.objects().first()).save()


def test_get_expenses(client):
    rv = client.get('/expenses/')
    assert isinstance(json.loads(rv.get_data(as_text=True)), list)


def test_get_expense(client):
    expense = Expense.objects[0]
    rv = client.get('/expenses/{}'.format(expense.id))
    assert isinstance(json.loads(rv.get_data(as_text=True)), dict)


def test_get_expense_404(client):
    invalid_id = '5b6d42132c8884b302632182'
    rv = client.get('/expenses/{}'.format(invalid_id))
    assert rv.status_code == 404
