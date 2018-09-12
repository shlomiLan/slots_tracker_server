import json
import os

import gspread
from oauth2client.service_account import ServiceAccountCredentials

from slots_tracker_server import app

start_column = 'A'
end_column = 'G'


def init_connection():
    credentials_data = os.environ.get('GSHEET_CREDENTIALS')
    if not credentials_data:
        raise KeyError('No credentials data, missing environment variable')

    credentials_data = json.loads(credentials_data)
    # Fix the 'private_key' escaping
    credentials_data['private_key'] = credentials_data.get('private_key').encode().decode('unicode-escape')
    scopes = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(credentials_data, scopes)
    return gspread.authorize(credentials)


def get_worksheet():
    gc = init_connection()
    return gc.open_by_key(app.config.get('GSHEET_ID')).sheet1


def write_expense(expense):
    wks = get_worksheet()
    headers = get_headers(wks)
    new_index = find_last_row(wks) + 1
    cell_list = wks.range('{start_column}{new_index}:{end_column}{new_index}'.format(
        start_column=start_column, new_index=new_index, end_column=end_column))

    for i, header in enumerate(headers):
        # Leave as expense[header.value], so if field not found we get an error
        cell_list[i].value = expense[header.value]

    wks.update_cells(cell_list)


def clean_expense_for_write(expense_as_json, expense):
    expense_as_json['pay_method'] = expense.pay_method.name
    expense_as_json['category'] = expense.category.name
    expense_as_json['one_time'] = 'One time' if expense.one_time else 'Regular'


def find_last_row(wks):
    return len(wks.col_values(2))


def get_headers(wks):
    return wks.range('{}1:{}1'.format(start_column, end_column))


def get_all_data(wks):
    return wks.get_all_values()


def end_column_as_number():
    return ord(end_column.lower()) - 96
