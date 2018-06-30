# system modules
import datetime

# 3rd party modules
from flask import abort
from mongoengine import *
from bson.json_util import dumps
from bson.objectid import ObjectId
from bson.errors import InvalidId

from slots_tracker.db import db
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
    expenses = db.expense.find()
    return dumps(expenses)


def read_one(expense_id):
    """
    This function responds to a request for /api/expense/{expenses_id}
    with one matching expense from expenses list
    :param expense_id: id of the expense to find
    :return:           expense matching id
    """
    object_id = convert_to_object_id(expense_id)

    if object_id:
        # Does the expense exist in the DB
        expense = db.expense.find_one({'_id': object_id})
        if expense:
            return dumps(expense)
        # otherwise, raise an error
        else:
            abort(404, 'Expense with id {} not found'.format(expense_id))
    else:
        abort(404, '{} is not a valid object ID'.format(expense_id))


def convert_to_object_id(expense_id):
    try:
        # Does it a valid ID
        return ObjectId(expense_id)
    except InvalidId:
        return None
