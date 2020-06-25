import os
from pytest import raises

from slots_tracker_server.utils import BASEDIR
from slots_tracker_server.models import PayMethods
from slots_tracker_server.parser import LOCAL_EXPENSES_KEY, IsracardParser, ABROAD_EXPENSES_KEY, \
    ABROAD_IN_LOCAL_CURRENCY_EXPENSES_KEY

FIRST_SECTION_START_INX = 24
FIRST_SECTION_END_INX = 70
SECOND_SECTION_START_INX = 86

TOTAL_NEW_EXPENSES = 49
TOTAL_NEW_CATEGORIES = 5

FILEPATH = os.path.join(BASEDIR, 'slots_tracker_server', 'tests', 'test_data', 'isracard.xlsx')


def test_get_index():
    isracard_parser = IsracardParser(FILEPATH)
    assert isracard_parser.find_inx(keyword=LOCAL_EXPENSES_KEY, is_start=True) == FIRST_SECTION_START_INX

    assert isracard_parser.find_inx(keyword=ABROAD_EXPENSES_KEY, is_start=False) == FIRST_SECTION_END_INX

    assert isracard_parser.find_inx(keyword=ABROAD_IN_LOCAL_CURRENCY_EXPENSES_KEY, is_start=True) == SECOND_SECTION_START_INX


def test_parse_file():
    # TODO: move to init function
    isracard_parser = IsracardParser(FILEPATH)
    new_expenses, new_categories = isracard_parser.parse_file()
    assert len(new_expenses) == TOTAL_NEW_EXPENSES
    assert len(new_categories) == TOTAL_NEW_CATEGORIES


def test_many_pay_methods_with_same_digits():
    PayMethods(name='new pay 1234').save()
    with raises(Exception):
        IsracardParser(FILEPATH)


def test_no_pay_methods_with_same_digits():
    original_name = 'Parser 1234'
    pay_method = PayMethods.objects.get(name=original_name)
    pay_method.name = 'name without numbers'
    pay_method.save()

    with raises(Exception):
        IsracardParser(FILEPATH)

    pay_method.name = original_name
    pay_method.save()
