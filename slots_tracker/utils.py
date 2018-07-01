# 3rd party modules
from flask import abort
from bson.objectid import ObjectId
from bson.errors import InvalidId


def convert_to_object_id(func):
    def wrapper_func(*args, **kwargs):
        id = kwargs.get('id')
        try:
            # Does it a valid ID - call the original fuction with the class and the new id
            return func(args[0], ObjectId(id))
        except InvalidId:
            abort(400, '{} is not a valid object ID'.format(id))

    return wrapper_func
