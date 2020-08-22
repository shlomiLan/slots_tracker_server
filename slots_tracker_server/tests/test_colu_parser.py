import json
import os

import pytest

from slots_tracker_server.parser import ColuParser
from slots_tracker_server.utils import BASEDIR


TEST_DATA_FOLDER = os.path.join(BASEDIR, 'slots_tracker_server', 'tests', 'test_data')
COLU_FOLDER = os.path.join(TEST_DATA_FOLDER, 'colu')
COLU_MESSAGE_FILEPATH = os.path.join(COLU_FOLDER, 'test.json')
COLU_MESSAGE_WITH_UNKNOWN_CURRENCY_FILEPATH = os.path.join(COLU_FOLDER, 'test_unknown_currency.json')
TOTAL_NEW_EXPENSES_COLU = 1
TOTAL_NEW_CATEGORIES_COLU = 1

EXPENSE_NAME = 'Xxxxxx'
EXPENSE_DAY = '05'
EXPENSE_MONTH = '07'
EXPENSE_YEAR = '2020'
EXPENSE_DATE = f'{EXPENSE_DAY}/{EXPENSE_MONTH}/{EXPENSE_YEAR}'
EXPENSE_AMOUNT = '95.00'
EXPENSE_BUSINESS_NAME = 'סילון בר'


def test_message_parse():
    with open(COLU_MESSAGE_FILEPATH) as json_file:
        message_data = json.load(json_file)
        parser = ColuParser(message_data)
        new_expenses, new_categories = parser.parse_message()
        assert len(new_expenses) == TOTAL_NEW_EXPENSES_COLU
        assert len(new_categories) == TOTAL_NEW_CATEGORIES_COLU

        for exp in new_expenses:
            assert exp.amount == float(EXPENSE_AMOUNT)

            assert exp.timestamp.day == int(EXPENSE_DAY)
            assert exp.timestamp.month == int(EXPENSE_MONTH)
            assert exp.timestamp.year == int(EXPENSE_YEAR)

            assert exp.business_name == EXPENSE_BUSINESS_NAME

        parser = ColuParser(message_data)
        new_expenses, new_categories = parser.parse_message()
        assert len(new_expenses) == 0
        assert len(new_categories) == 0

    with open(COLU_MESSAGE_FILEPATH) as json_file:
        parser = ColuParser(json_file.read())
        new_expenses, new_categories = parser.parse_message()
        assert len(new_expenses) == 0
        assert len(new_categories) == 0


def test_message_parse_with_unknown_currency():
    with pytest.raises(Exception):
        with open(COLU_MESSAGE_WITH_UNKNOWN_CURRENCY_FILEPATH) as json_file:
            parser = ColuParser(json_file.read())
            parser.parse_message()


def test_message_attributes():
    with open(COLU_MESSAGE_FILEPATH) as json_file:
        parser = ColuParser(json_file.read())
        message_attributes = parser.get_message_attributes()

        assert message_attributes.get('name') == EXPENSE_NAME
        assert message_attributes.get('date') == EXPENSE_DATE
        assert message_attributes.get('amount') == EXPENSE_AMOUNT
        assert message_attributes.get('real_money') == parser.CURRENCY_NAME
        assert message_attributes.get('business_name') == EXPENSE_BUSINESS_NAME
