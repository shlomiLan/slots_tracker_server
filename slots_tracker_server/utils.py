import datetime
from typing import Tuple, Dict, Any, Union, Type

import pandas as pd
from bson.errors import InvalidId
from bson.objectid import ObjectId
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
from flask import abort
from flask.views import MethodView

from slots_tracker_server import app


def convert_to_object_id(str_id: str) -> Union[ObjectId]:
    if not str_id:
        abort(400, 'object ID can not be None')
    try:
        # Does it a valid ID - call the original function with the class and the new id
        return ObjectId(str_id)
    except InvalidId:
        abort(400, '{} is not a valid object ID'.format(str_id))


def object_id_to_str(object_id: ObjectId) -> str:
    return str(object_id)


def find_and_convert_object_id(obj: Dict[str, Any]) -> None:
    for k, v in obj.items():
        if isinstance(v, ObjectId):
            obj[k] = object_id_to_str(v)


def date_to_str(date) -> str:
    return str(date.date())


def find_and_convert_date(obj: Dict[str, Any]) -> None:
    for k, v in obj.items():
        if isinstance(v, datetime.datetime):
            obj[k] = date_to_str(v)


def register_api(view: Type[MethodView], endpoint: str, url: str, pk: str = 'id', pk_type: str = 'string') -> None:
    view_func = view.as_view(endpoint)
    app.add_url_rule(url, defaults={pk: None}, view_func=view_func, methods=['GET', ])
    app.add_url_rule(url, view_func=view_func, methods=['POST', ])
    app.add_url_rule('%s<%s:%s>' % (url, pk_type, pk), view_func=view_func, methods=['GET', 'PUT', 'DELETE'])


def clean_api_object(obj_data: Dict[str, Any]) -> None:
    if obj_data.get('_id'):
        # Remove the object ID from obj_data
        del obj_data['_id']


def get_bill_cycles(today: pd.datetime) -> Tuple[pd.datetime, pd.datetime, pd.datetime, pd.datetime]:
    # Case 4: 1-1-18
    if today.month == 1 and today.day < 10:
        previous_month, previous_year = 11, today.year - 1
        middle_month, middle_year = 12, today.year - 1
        next_month, next_year = 1, today.year
    # Case 5 and Case 2: 10-1-18, 1-2-18
    elif (today.month == 2 and today.day < 10) or (today.month == 1 and today.day >= 10):
        previous_month, previous_year = 12, today.year - 1
        middle_month, middle_year = 1, today.year
        next_month, next_year = 2, today.year

    # Case 6: 10-12-18
    elif today.month == 12 and today.day >= 10:
        previous_month, previous_year = 11, today.year
        middle_month, middle_year = 12, today.year
        next_month, next_year = 1, today.year + 1
    else:
        # Case 3: 1-9-18, 1-12-18
        if today.day < 10:
            previous_month, previous_year = today.month - 2, today.year
            middle_month, middle_year = today.month - 1, today.year
            next_month, next_year = today.month, today.year

        # Case 1: 10-11-18, 21-2-18, 21-11-18, 12-2-18
        else:
            previous_month, previous_year = today.month - 1, today.year
            middle_month, middle_year = today.month, today.year
            next_month, next_year = today.month + 1, today.year

    start_cycle1 = pd.datetime(previous_year, previous_month, 10)
    end_cycle1 = pd.datetime(middle_year, middle_month, 9)
    start_cycle2 = pd.datetime(middle_year, middle_month, 10)
    end_cycle2 = pd.datetime(next_year, next_month, 9)

    return start_cycle1, end_cycle1, start_cycle2, end_cycle2


def next_payment_date(current_date: str, payment: int = 1) -> datetime.datetime:
    return parse(current_date) + relativedelta(months=+payment)
