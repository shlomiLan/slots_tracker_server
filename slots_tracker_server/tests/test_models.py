import datetime

import pytest
from mongoengine.errors import FieldDoesNotExist, ValidationError

from slots_tracker_server.models import Expense, PayMethods, Categories


def test_field_does_not_exist():
    with pytest.raises(FieldDoesNotExist):
        Expense(amounta=200, description='Random stuff', pay_method=PayMethods.objects().first(),
                timestamp=datetime.datetime.utcnow, category=Categories.objects().first()).save()


def test_missing_required_field():
    with pytest.raises(ValidationError):
        Expense(amount=200, pay_method=PayMethods.objects().first(), category=Categories.objects().first()).save()
