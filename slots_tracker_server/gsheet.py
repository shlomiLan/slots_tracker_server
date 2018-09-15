import json
import os
import time

import gspread
from gspread.exceptions import APIError
from oauth2client.service_account import ServiceAccountCredentials

start_column = 'A'
end_column = 'G'
gsheet_write_counter = 0


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
    return gc.open_by_key(os.environ.get('GSHEET_ID')).worksheet('All data')


def write_expense(expense):
    wks = get_worksheet()
    headers = get_headers(wks)
    new_index = find_last_row(wks) + 1
    cell_list = wks.range('{start_column}{new_index}:{end_column}{new_index}'.format(
        start_column=start_column, new_index=new_index, end_column=end_column))

    for i, header in enumerate(headers):
        # Leave as expense[header.value], so if field not found we get an error
        expense_as_json = clean_expense_for_write(expense)
        cell_list[i].value = expense_as_json[header.value]

    update_with_retry(wks, cell_list=cell_list)


def clean_expense_for_write(expense):
    temp = expense.to_json()
    temp['pay_method'] = expense.pay_method.name
    temp['category'] = expense.category.name
    temp['one_time'] = 'One time' if expense.one_time else 'Regular'
    if '-' in temp['timestamp']:
        year, month, day = temp['timestamp'].split('-')
        temp['timestamp'] = f'{month}/{day}/{year}'

    return temp


def find_last_row(wks):
    return len(wks.col_values(2))


def get_headers(wks):
    return wks.range('{}1:{}1'.format(start_column, end_column))


def get_all_data(wks):
    return wks.get_all_values()


def end_column_as_number():
    return ord(end_column.lower()) - 96


def update_with_retry(wks, row=None, col=None, value=None, cell_list=None):
    global gsheet_write_counter
    retries = 3

    while retries:
        if gsheet_write_counter > 90:
            time.sleep(100)
            gsheet_write_counter = 0

        try:
            gsheet_write_counter += 1
            if cell_list:
                wks.update_cells(cell_list)
            elif row is not None and col is not None and value is not None:
                wks.update_cell(row, col, value)
            else:
                raise ValueError(f'No match was found in the receiving parameters: row: {row}, col: {col}, '
                                 f'value: {value}, cell_list: {cell_list}')

            # No need to try again
            retries = 0
        except APIError as e:
            # Try again only if error code is 429
            if e.response.status_code == 429:
                print(f'Going to sleep, attempt NO. {3 - retries + 1}')
                time.sleep(100)
                retries -= 1
            else:
                raise e
