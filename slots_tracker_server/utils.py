# 3rd party modules
import datetime

from bson.errors import InvalidId
from bson.objectid import ObjectId
from flask import abort

from slots_tracker_server import app


def convert_to_object_id(str_id):
    try:
        # Does it a valid ID - call the original function with the class and the new id
        return ObjectId(str_id)
    except InvalidId:
        abort(400, '{} is not a valid object ID'.format(str_id))


def object_id_to_str(obj):
    for k, v in obj.items():
        if isinstance(v, ObjectId):
            obj[k] = str(v)

    return obj


def convert_date(obj):
    for k, v in obj.items():
        if isinstance(v, datetime.datetime):
            obj[k] = str(v.date())

    return obj


def register_api(view, endpoint, url, pk='id', pk_type='string'):
    view_func = view.as_view(endpoint)
    app.add_url_rule(url, defaults={pk: None}, view_func=view_func, methods=['GET', ])
    app.add_url_rule(url, view_func=view_func, methods=['POST', ])
    app.add_url_rule('%s<%s:%s>' % (url, pk_type, pk), view_func=view_func, methods=['GET', 'PUT', 'DELETE'])
