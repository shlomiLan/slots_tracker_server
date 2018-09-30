import datetime
from typing import Tuple

import pandas as pd
from bson.errors import InvalidId
from bson.objectid import ObjectId
from flask import abort

from slots_tracker_server import app


def convert_to_object_id(str_id):
    if not str_id:
        abort(400, 'object ID can not be None')
    try:
        # Does it a valid ID - call the original function with the class and the new id
        return ObjectId(str_id)
    except InvalidId:
        abort(400, '{} is not a valid object ID'.format(str_id))


def object_id_to_str(object_id):
    return str(object_id)


def find_and_convert_object_id(obj):
    for k, v in obj.items():
        if isinstance(v, ObjectId):
            obj[k] = object_id_to_str(v)


def date_to_str(date):
    return str(date.date())


def find_and_convert_date(obj):
    for k, v in obj.items():
        if isinstance(v, datetime.datetime):
            obj[k] = date_to_str(v)


def register_api(view, endpoint, url, pk='id', pk_type='string'):
    view_func = view.as_view(endpoint)
    app.add_url_rule(url, defaults={pk: None}, view_func=view_func, methods=['GET', ])
    app.add_url_rule(url, view_func=view_func, methods=['POST', ])
    app.add_url_rule('%s<%s:%s>' % (url, pk_type, pk), view_func=view_func, methods=['GET', 'PUT', 'DELETE'])


def clean_api_object(obj_data):
    if obj_data.get('_id'):
        # Remove the object ID from obj_data
        del obj_data['_id']


def get_10th(today: pd.datetime) -> Tuple[pd.datetime, pd.datetime, pd.datetime]:
    # Examples: 10-12-2018, 01-12-2018
    if today.day <= 10 and today.month == 12:
        previous_month, previous_year = today.month - 1, today.year
        current_month, current_year = today.month, today.year
        next_month, next_year = 1, today.year + 1

    # Examples: 10-01-2018, 1-1-2018
    elif today.day <= 10 and today.month == 1:
        previous_month, previous_year = 12, today.year - 1
        current_month, current_year = 1, today.year
        next_month, next_year = today.month + 1, today.year

    # Examples: 21-02-2018
    elif today.day > 10 and today.month == 2:
        previous_month, previous_year = 12, today.year - 1
        current_month, current_year = 1, today.year
        next_month, next_year = today.month, today.year

    # Examples: 10-11-2018, 21-11-2018, 01-09-2018
    else:
        previous_month, previous_year = today.month - 1, today.year
        current_month, current_year = today.month, today.year
        next_month, next_year = today.month + 1, today.year

    next_10th = pd.datetime(next_year, next_month, 10)
    current_10th = pd.datetime(current_year, current_month, 10)
    previous_10th = pd.datetime(previous_year, previous_month, 10)

    return previous_10th, current_10th, next_10th
