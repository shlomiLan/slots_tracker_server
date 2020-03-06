from datetime import datetime

import pytest
from mongoengine.errors import FieldDoesNotExist, ValidationError

from slots_tracker_server.models import Expense, PayMethods, Categories


def test_field_does_not_exist():
    with pytest.raises(FieldDoesNotExist):
        Expense(amounta=200, pay_method=PayMethods.objects().first(), timestamp=datetime.utcnow, category=Categories.objects().first()).save()


def test_missing_required_field():
    with pytest.raises(ValidationError):
        Expense(amount=200, pay_method=PayMethods.objects().first(), category=Categories.objects().first()).save()


def test_save():
    pay_method = PayMethods.objects().first()
    category = Categories.objects().first()
    pay_method_instances = pay_method.instances
    category_instances = category.instances
    Expense(amount=200, pay_method=pay_method, timestamp=datetime.utcnow,
            category=category).save()

    assert pay_method.instances == pay_method_instances + 1
    assert category.instances == category_instances + 1
