import json
import os

import gspread
from oauth2client.service_account import ServiceAccountCredentials

from slots_tracker_server import app

start_column = 'A'
end_column = 'F'


def init_connection():
    credentials_data = json.loads(os.environ['GSHEET_CREDENTIALS'])
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
        cell_list[i].value = expense.get(header.value)

    wks.update_cells(cell_list)


def find_last_row(wks):
    return len(wks.col_values(1))


def get_headers(wks):
    return wks.range('{}1:{}1'.format(start_column, end_column))
