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
    value_list = []

    expense_as_json = clean_expense_for_write(expense)
    for i, header in enumerate(headers):
        value_list.append(expense_as_json[header.value])

    update_with_retry(wks, index=new_index, value_list=value_list)


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


def update_with_retry(wks, row=None, col=None, value=None, index=None, value_list=None):
    global gsheet_write_counter
    retries = 3

    while retries:
        if gsheet_write_counter > 90:
            time.sleep(100)
            gsheet_write_counter = 0

        try:
            gsheet_write_counter += 1
            if value_list and index:
                wks.insert_row(value_list, index=index, value_input_option='USER_ENTERED')
            elif row is not None and col is not None and value is not None:
                wks.update_cell(row, col, value)
            else:
                raise ValueError(f'No match was found in the receiving parameters: row: {row}, col: {col}, '
                                 f'value: {value}, index: {index}, value_list: {value_list}')

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
