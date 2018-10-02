import datetime

import pandas as pd
import pytest
from bson import ObjectId
from werkzeug.exceptions import BadRequest

from slots_tracker_server.utils import convert_to_object_id, find_and_convert_object_id, find_and_convert_date, \
    get_bill_cycles

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

    find_and_convert_object_id(data)
    assert expected_data == data


def test_object_id_to_str_none():
    with pytest.raises(BadRequest):
        convert_to_object_id(None)


def test_convert_date():
    data = dict(time=datetime.datetime(2018, 8, 10, 9, 20, 57, 983368))
    expected_data = dict(time='2018-08-10')
    find_and_convert_date(data)
    assert expected_data == data


def test_get_bill_cycles():
    start_cycle1, end_cycle1, start_cycle2, end_cycle2 = get_bill_cycles(pd.datetime(2018, 11, 10))
    assert start_cycle1 == pd.datetime(2018, 10, 10)
    assert end_cycle1 == pd.datetime(2018, 11, 9)
    assert start_cycle2 == pd.datetime(2018, 11, 10)
    assert end_cycle2 == pd.datetime(2018, 12, 9)

    start_cycle1, end_cycle1, start_cycle2, end_cycle2 = get_bill_cycles(pd.datetime(2018, 12, 10))
    assert start_cycle1 == pd.datetime(2018, 11, 10)
    assert end_cycle1 == pd.datetime(2018, 12, 9)
    assert start_cycle2 == pd.datetime(2018, 12, 10)
    assert end_cycle2 == pd.datetime(2019, 1, 9)

    start_cycle1, end_cycle1, start_cycle2, end_cycle2 = get_bill_cycles(pd.datetime(2018, 1, 10))
    assert start_cycle1 == pd.datetime(2017, 12, 10)
    assert end_cycle1 == pd.datetime(2018, 1, 9)
    assert start_cycle2 == pd.datetime(2018, 1, 10)
    assert end_cycle2 == pd.datetime(2018, 2, 9)

    start_cycle1, end_cycle1, start_cycle2, end_cycle2 = get_bill_cycles(pd.datetime(2018, 2, 21))
    assert start_cycle1 == pd.datetime(2018, 1, 10)
    assert end_cycle1 == pd.datetime(2018, 2, 9)
    assert start_cycle2 == pd.datetime(2018, 2, 10)
    assert end_cycle2 == pd.datetime(2018, 3, 9)

    start_cycle1, end_cycle1, start_cycle2, end_cycle2 = get_bill_cycles(pd.datetime(2018, 11, 21))
    assert start_cycle1 == pd.datetime(2018, 10, 10)
    assert end_cycle1 == pd.datetime(2018, 11, 9)
    assert start_cycle2 == pd.datetime(2018, 11, 10)
    assert end_cycle2 == pd.datetime(2018, 12, 9)

    start_cycle1, end_cycle1, start_cycle2, end_cycle2 = get_bill_cycles(pd.datetime(2018, 9, 1))
    assert start_cycle1 == pd.datetime(2018, 7, 10)
    assert end_cycle1 == pd.datetime(2018, 8, 9)
    assert start_cycle2 == pd.datetime(2018, 8, 10)
    assert end_cycle2 == pd.datetime(2018, 9, 9)

    start_cycle1, end_cycle1, start_cycle2, end_cycle2 = get_bill_cycles(pd.datetime(2018, 12, 1))
    assert start_cycle1 == pd.datetime(2018, 10, 10)
    assert end_cycle1 == pd.datetime(2018, 11, 9)
    assert start_cycle2 == pd.datetime(2018, 11, 10)
    assert end_cycle2 == pd.datetime(2018, 12, 9)

    start_cycle1, end_cycle1, start_cycle2, end_cycle2 = get_bill_cycles(pd.datetime(2018, 1, 1))
    assert start_cycle1 == pd.datetime(2017, 11, 10)
    assert end_cycle1 == pd.datetime(2017, 12, 9)
    assert start_cycle2 == pd.datetime(2017, 12, 10)
    assert end_cycle2 == pd.datetime(2018, 1, 9)

    start_cycle1, end_cycle1, start_cycle2, end_cycle2 = get_bill_cycles(pd.datetime(2018, 2, 1))
    assert start_cycle1 == pd.datetime(2017, 12, 10)
    assert end_cycle1 == pd.datetime(2018, 1, 9)
    assert start_cycle2 == pd.datetime(2018, 1, 10)
    assert end_cycle2 == pd.datetime(2018, 2, 9)

    start_cycle1, end_cycle1, start_cycle2, end_cycle2 = get_bill_cycles(pd.datetime(2018, 2, 10))
    assert start_cycle1 == pd.datetime(2018, 1, 10)
    assert end_cycle1 == pd.datetime(2018, 2, 9)
    assert start_cycle2 == pd.datetime(2018, 2, 10)
    assert end_cycle2 == pd.datetime(2018, 3, 9)
