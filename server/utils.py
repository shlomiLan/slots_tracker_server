# 3rd party modules
from flask import abort
from bson.objectid import ObjectId
from bson.errors import InvalidId

from server import app


def convert_to_object_id(id):
    try:
        # Does it a valid ID - call the original fuction with the class and the new id
        return ObjectId(id)
    except InvalidId:
        abort(400, '{} is not a valid object ID'.format(id))


def register_api(view, endpoint, url, pk='id', pk_type='string'):
    view_func = view.as_view(endpoint)
    app.add_url_rule(url, defaults={pk: None}, view_func=view_func, methods=['GET', ])
    app.add_url_rule(url, view_func=view_func, methods=['POST', ])
    app.add_url_rule('%s<%s:%s>' % (url, pk_type, pk), view_func=view_func, methods=['GET', 'PUT', 'DELETE'])
