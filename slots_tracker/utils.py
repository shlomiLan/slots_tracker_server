# 3rd party modules
from flask import abort
from bson.objectid import ObjectId
from bson.errors import InvalidId


def convert_to_object_id(func):
    def wrapper_func(*args):
        expense_id = args[0]
        try:
            # Does it a valid ID
            return func(ObjectId(expense_id))
        except InvalidId:
            abort(400, '{} is not a valid object ID'.format(expense_id))

    return wrapper_func
