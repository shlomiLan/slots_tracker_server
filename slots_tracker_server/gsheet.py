import json
import os
import time

import gspread
from gspread.exceptions import APIError
from oauth2client.service_account import ServiceAccountCredentials

from slots_tracker_server.utils import object_id_to_str

START_COLUMN = 'A'
END_COLUMN = 'G'
DATE_INDEX = 3
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


def update_expense(expense):
    wks = get_worksheet()
    headers = get_headers(wks)
    cell = wks.find(object_id_to_str(expense.id))
    expense_row = cell.row
    expense_gsheet_data = get_expense_by_row(wks, expense_row)

    expense_as_json = clean_expense_for_write(expense)
    updates = 0
    for i, header in enumerate(headers):
        new_expense_value = str(expense_as_json[header.value])
        existing_value = expense_gsheet_data[i].value

        if new_expense_value != existing_value:
            if header.value == 'timestamp':
                if compare_dates(new_expense_value, existing_value):
                    continue
            elif header.value == 'amount':
                if compare_floats(new_expense_value, existing_value):
                    continue

            updates += 1
            print(f'new_expense_value: {new_expense_value}')
            print(f'existing_value: {existing_value}')
            print(f'Updating row: {expense_row}, col: {i + 1}, with value: {new_expense_value}')
            update_with_retry(wks, row=expense_row, col=i + 1, value=new_expense_value)

    return updates


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
    return wks.range(f'{START_COLUMN}1:{END_COLUMN}1')


def get_expense_by_row(wks, row):
    return wks.range(f'{START_COLUMN}{row}:{END_COLUMN}{row}')


def get_all_data(wks):
    return wks.get_all_values()


def end_column_as_number():
    return ord(END_COLUMN.lower()) - 96


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


def compare_dates(expense_date, gsheet_date):
    month1, day1, year1 = expense_date.split('/')
    day2, month2, year2 = gsheet_date.split('/')

    year2 = f'20{year2}'
    return int(year1) == int(year2) and int(month1) == int(month2) and int(day1) == int(day2)


def compare_floats(expense_number, gsheet_number):
    try:
        return float(expense_number) == float(gsheet_number.replace(',', ''))
    except ValueError:
        return True
