from bson.objectid import ObjectId
from bson.errors import InvalidId


def convert_to_object_id(expense_id):
    try:
        # Does it a valid ID
        return ObjectId(expense_id)
    except InvalidId:
        return None
