import datetime

import pytest
from mongoengine.errors import FieldDoesNotExist

from slots_tracker_server.expense import Expense, PayMethods


# from server.board import Board


def test_empty_db(client):
    """Start with a blank database."""
    rv = client.get('/expenses/')
    assert rv.get_json() is None


def test_create_expense():
    response = Expense(amount=200, description='Random stuff', pay_method=PayMethods.objects().first(),
                       timestamp=datetime.datetime.utcnow).save()

    # We got a new object
    assert response is not None


def test_field_does_not_exist():
    # We got a error code
    with pytest.raises(FieldDoesNotExist):
        Expense(amounta=200, description='Random stuff', pay_method=PayMethods.objects().first()).save()
