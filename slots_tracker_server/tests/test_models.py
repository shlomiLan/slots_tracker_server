import pytest
from mongoengine.errors import FieldDoesNotExist

from slots_tracker_server.models import Expense, PayMethods


def test_field_does_not_exist():
    with pytest.raises(FieldDoesNotExist):
        Expense(amounta=200, description='Random stuff', pay_method=PayMethods.objects().first()).save()

# TODO: add test for missing field
