import datetime

import pytest
from bson import ObjectId
from werkzeug.exceptions import BadRequest

from slots_tracker_server.utils import convert_to_object_id, object_id_to_str, convert_date

VALID_ID = '5b5c8a2b2c88848042426dff'
INVALID_ID = '5b5c8a2b2c88848042426dffa'


def test_convert_valid_id():
    assert isinstance(convert_to_object_id(VALID_ID), ObjectId)


def test_convert_invalid_id():
    with pytest.raises(BadRequest):
        convert_to_object_id(INVALID_ID)


def test_object_id_to_str():
    data = dict(_id=ObjectId("5b5c8a2b2c88848042426dff"), pay_method=ObjectId("5b5c8a2b2c88848042426dfd"))
    expected_data = dict(_id='5b5c8a2b2c88848042426dff', pay_method='5b5c8a2b2c88848042426dfd')

    assert expected_data == object_id_to_str(data)


def test_convert_date():
    data = dict(time=datetime.datetime(2018, 8, 10, 9, 20, 57, 983368))
    expected_data = dict(time='2018-08-10')
    assert expected_data == convert_date(data)
