import os

import pytest
from pytest import raises

from slots_tracker_server.utils import BASEDIR
from slots_tracker_server.models import PayMethods
from slots_tracker_server.parser import IsracardParser, VisaParser, get_parser_from_file_path

FIRST_SECTION_START_INX = 24
FIRST_SECTION_END_INX = 70
SECOND_SECTION_START_INX = 86

TOTAL_NEW_EXPENSES_ISRACARD = 49
TOTAL_NEW_CATEGORIES_ISRACARD = 5

TOTAL_NEW_EXPENSES_VISA = 8
TOTAL_NEW_CATEGORIES_VISA = 7

TEST_DATA_FOLDER = os.path.join(BASEDIR, 'slots_tracker_server', 'tests', 'test_data')
ISRACARD_FILEPATH = os.path.join(TEST_DATA_FOLDER, 'isracard', 'isracard.xlsx')
VISA_FILEPATH = os.path.join(TEST_DATA_FOLDER, 'visa', '1234', '02_2020.xls')
UNKNOWN_FILEPATH = os.path.join(TEST_DATA_FOLDER, 'xxx.xlsx')


def test_get_index():
    isracard_parser = IsracardParser(ISRACARD_FILEPATH)
    assert isracard_parser.find_inx(keywords=[isracard_parser.LOCAL_EXPENSES_KEY], is_start=True) == FIRST_SECTION_START_INX  # noqa

    assert isracard_parser.find_inx(keywords=[isracard_parser.ABROAD_EXPENSES_IN_DOLLARS_KEY], is_start=False) == FIRST_SECTION_END_INX  # noqa

    assert isracard_parser.find_inx(keywords=[isracard_parser.ABROAD_IN_LOCAL_CURRENCY_EXPENSES_KEY], is_start=True) == SECOND_SECTION_START_INX  # noqa


def test_parse_file():
    parser = get_parser_from_file_path(ISRACARD_FILEPATH)
    new_expenses, new_categories = parser.parse_file()
    assert len(new_expenses) == TOTAL_NEW_EXPENSES_ISRACARD
    assert len(new_categories) == TOTAL_NEW_CATEGORIES_ISRACARD

    # Try to reload same file - should be no changes
    parser = get_parser_from_file_path(ISRACARD_FILEPATH)
    new_expenses, new_categories = parser.parse_file()
    assert len(new_categories) == len(new_expenses) == 0

    # Parser another file
    parser = get_parser_from_file_path(VISA_FILEPATH)
    new_expenses, new_categories = parser.parse_file()
    assert len(new_expenses) == TOTAL_NEW_EXPENSES_VISA
    assert len(new_categories) == TOTAL_NEW_CATEGORIES_VISA


def test_many_pay_methods_with_same_digits():
    PayMethods(name='new pay 1234').save()
    with raises(Exception):
        IsracardParser(ISRACARD_FILEPATH)


def test_no_pay_methods_with_same_digits():
    original_name = 'Parser 1234'
    pay_method = PayMethods.objects.get(name=original_name)
    pay_method.name = 'name without numbers'
    pay_method.save()

    with raises(Exception):
        IsracardParser(ISRACARD_FILEPATH)

    pay_method.name = original_name
    pay_method.save()


def test_get_parser_from_file_path():
    assert isinstance(get_parser_from_file_path(ISRACARD_FILEPATH), IsracardParser)
    assert isinstance(get_parser_from_file_path(VISA_FILEPATH), VisaParser)

    with pytest.raises(Exception):
        get_parser_from_file_path(UNKNOWN_FILEPATH)
