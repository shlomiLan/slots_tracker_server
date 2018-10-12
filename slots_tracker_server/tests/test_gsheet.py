from unittest import mock

import pytest
from gspread import Worksheet
from gspread.client import Client

import slots_tracker_server.gsheet as gsheet
from slots_tracker_server.utils import clean_api_object


def test_init_connection():
    assert isinstance(gsheet.init_connection(), Client)


def test_init_connection_no_credentials():
    with mock.patch.dict('os.environ', {'GSHEET_CREDENTIALS': ''}):
        with pytest.raises(KeyError):
            gsheet.init_connection()


def test_get_worksheet():
    assert isinstance(gsheet.get_worksheet(), Worksheet)


def test_find_last_row():
    wks = gsheet.get_worksheet()
    assert gsheet.find_last_row(wks) > 0


def test_get_header():
    wks = gsheet.get_worksheet()
    assert isinstance(gsheet.get_headers(wks), list)


def test_get_all_data():
    wks = gsheet.get_worksheet()
    assert isinstance(gsheet.get_all_data(wks), list)


def test_write_expense():
    wks = gsheet.get_worksheet()
    last_row = gsheet.find_last_row(wks)
    # Leave here to prevent circular import
    from slots_tracker_server.models import Expense
    expense = Expense.objects[0]
    gsheet.write_doc(expense)

    # Test that we have a new line in the spreadsheet
    new_last_row = gsheet.find_last_row(wks)
    assert new_last_row == last_row + 1


def test_end_column_as_number():
    assert gsheet.end_column_as_number() == 7


def test_update_with_retry_invalid_params():
    wks = gsheet.get_worksheet()
    with pytest.raises(ValueError):
        gsheet.update_with_retry(wks, row=1, value=10)


def test_update_expense():
    from slots_tracker_server.models import Expense
    expense_data = Expense.objects[0].to_json()
    clean_api_object(expense_data)
    new_expense = Expense(**expense_data).save()
    gsheet.write_doc(new_expense)
    new_expense.amount = 9999
    num_of_updates = gsheet.update_doc(new_expense)

    assert num_of_updates == 1
