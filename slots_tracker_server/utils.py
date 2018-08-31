import datetime

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

    return obj


def date_to_str(date):
    return str(date.date())


def find_and_convert_date(obj):
    for k, v in obj.items():
        if isinstance(v, datetime.datetime):
            obj[k] = date_to_str(v)

    return obj


def register_api(view, endpoint, url, pk='id', pk_type='string'):
    view_func = view.as_view(endpoint)
    app.add_url_rule(url, defaults={pk: None}, view_func=view_func, methods=['GET', ])
    app.add_url_rule(url, view_func=view_func, methods=['POST', ])
    app.add_url_rule('%s<%s:%s>' % (url, pk_type, pk), view_func=view_func, methods=['GET', 'PUT', 'DELETE'])
