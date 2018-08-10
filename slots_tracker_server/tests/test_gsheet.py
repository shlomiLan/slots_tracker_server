from unittest import mock

import pytest
from bson import json_util
from gspread import Worksheet
from gspread.client import Client

from slots_tracker_server.gsheet import init_connection, get_worksheet, find_last_row, get_headers, \
    clean_expense_for_write


def test_init_connection():
    assert isinstance(init_connection(), Client)


def test_init_connection_no_credentials():
    with mock.patch.dict('os.environ', {'GSHEET_CREDENTIALS': ''}):
        with pytest.raises(KeyError):
            init_connection()


def test_get_worksheet():
    assert isinstance(get_worksheet(), Worksheet)


def test_find_last_row():
    wks = get_worksheet()
    assert find_last_row(wks) > 0


def test_get_header():
    wks = get_worksheet()
    assert isinstance(get_headers(wks), list)


def test_write_expense():
    wks = get_worksheet()
    last_row = find_last_row(wks)
    # Leave here to prevent circular import
    from slots_tracker_server.gsheet import write_expense
    from slots_tracker_server.expense import Expense
    expense = Expense.objects[0]
    expense_as_json = json_util.loads(expense.to_json())
    clean_expense_for_write(expense_as_json, expense)
    write_expense(expense_as_json)

    # Test that we have a new line in the spreadsheet
    new_last_row = find_last_row(wks)
    assert new_last_row == last_row + 1
