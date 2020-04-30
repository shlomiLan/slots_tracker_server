from datetime import datetime

import pytest
from mongoengine.errors import FieldDoesNotExist, ValidationError

from slots_tracker_server.models import Expense, PayMethods, Categories, WorkGroups
from slots_tracker_server.tests.conftest import AMOUNT


def test_field_does_not_exist():
    with pytest.raises(FieldDoesNotExist):
        Expense(amounta=AMOUNT, pay_method=PayMethods.objects().first(), timestamp=datetime.utcnow,
                category=Categories.objects().first(), work_group=WorkGroups.objects().first()).save()


def test_missing_required_field():
    with pytest.raises(ValidationError):
        Expense(amount=AMOUNT, pay_method=PayMethods.objects().first(), category=Categories.objects().first(),
                work_group=WorkGroups.objects().first()).save()


def test_save():
    pay_method = PayMethods.objects().first()
    category = Categories.objects().first()
    work_group = WorkGroups.objects().first()
    pay_method_instances = pay_method.instances
    category_instances = category.instances
    work_group_instances = work_group.instances

    Expense(amount=AMOUNT, pay_method=pay_method, timestamp=datetime.utcnow, category=category,
            work_group=work_group).save()

    assert pay_method.instances == pay_method_instances + 1
    assert category.instances == category_instances + 1
    assert work_group.instances == work_group_instances + 1
