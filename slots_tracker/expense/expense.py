# system modules
import datetime

# 3rd party modules
from flask import abort
from mongoengine import *
from bson.objectid import ObjectId
from bson.errors import InvalidId

from slots_tracker.pay_methods import PayMethods


class Expense(Document):
    amount = IntField()
    descreption = StringField(required=True, max_length=200)
    pay_method = ReferenceField(PayMethods, required=True)
    timestamp = DateTimeField(default=datetime.datetime.utcnow)


def create(expense):
    new_expense = Expense(**expense).save()
    return read_one(new_expense.id), 201


def read_all():
    return Expense.objects.to_json()


def read_one(expense_id):
    """
    This function responds to a request for /api/expense/{expenses_id}
    with one matching expense from expenses list
    :param expense_id: id of the expense to find
    :return:           expense matching id
    """
    object_id = convert_to_object_id(expense_id)

    if object_id:
        try:
            # Does the expense exist in the DB
            return Expense.objects.get(id=object_id).to_json()
        except DoesNotExist:
            abort(404, 'Expense with id {} not found'.format(expense_id))
    else:
        abort(400, '{} is not a valid object ID'.format(expense_id))


def convert_to_object_id(expense_id):
    try:
        # Does it a valid ID
        return ObjectId(expense_id)
    except InvalidId:
        return None
