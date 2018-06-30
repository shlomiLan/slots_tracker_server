# stsyem modules
import datetime
# 3rd party modules
import pytest
from werkzeug.exceptions import NotFound, BadRequest
from bson.json_util import loads
from bson.objectid import ObjectId

from slots_tracker.expense import create, read_all, read_one, convert_to_object_id
from slots_tracker.pay_methods import PayMethods


# TODO: Chnage test to not use the real DB
def test_create_expense():
    response = create(dict(amount=200, descreption='Random stuff', pay_method=PayMethods.objects()[0],
                           timestamp=datetime.datetime.utcnow))
    # We got a success code
    assert response[1] == 201


def test_create_expense_no_date():
    response = create(dict(amount=200, descreption='Random stuff',
                           pay_method=PayMethods.objects()[0]))
    # We got a success code
    assert response[1] == 201
    assert 'timestamp' in response[0]


# TODO: after chaning DB add logic to test the contant
def test_read_all():
    assert read_all() is not None


def test_read_one():
    expense_id = '5b376318c54d2d6a947bea43'
    new_expense_id_as_str = str(loads(read_one(expense_id)).get('_id'))
    assert new_expense_id_as_str == expense_id


def test_read_one_invaild_id():
    # We got a error code
    with pytest.raises(BadRequest):
        expense_id = '5b376318c54d2d6a947bea43lllll'
        read_one(expense_id)


def test_read_one_id_not_in_db():
    # We got a error code
    with pytest.raises(NotFound):
        expense_id = '5b376318c54d2d6a947bea41'
        read_one(expense_id)


def test_convert_to_object_id_valid():
    expense_id = '5b376318c54d2d6a947bea43'
    assert isinstance(convert_to_object_id(expense_id), ObjectId)


def test_convert_to_object_id_invalid():
    expense_id = '5b376318c54d2d6a947bea43lllll'
    assert convert_to_object_id(expense_id) is None
