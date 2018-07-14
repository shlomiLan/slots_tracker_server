# system modules
import json
import datetime

# 3rd party modules
from flask.views import MethodView
from flask import request
from mongoengine import *

from server.board import Board
from server.utils import convert_to_object_id


# Find way to add data with migration script
class PayMethods(Document):
    name = StringField(required=True, max_length=200)


class Expense(Document):
    amount = IntField()
    descreption = StringField(required=True, max_length=200)
    pay_method = ReferenceField(PayMethods, required=True)
    timestamp = DateTimeField(default=datetime.datetime.utcnow)
    board = ReferenceField(Board, required=True)


class ExpenseAPI(MethodView):
    def get(self, expense_id):
        if expense_id is None:
            return Expense.objects.to_json()
        else:
            object_id = convert_to_object_id(expense_id)
            try:
                # Does the expense exist in the DB
                return Expense.objects.get(id=object_id).to_json()
            except DoesNotExist:
                abort(404, 'Expense with id {} not found'.format(object_id))

    def post(self):
        expense_data = json.loads(request.data)
        return Expense(**expense_data).save().to_json(), 201

    def delete(self, expense_id):
        # delete a single user
        pass

    def put(self, expense_id):
        # update a single user
        pass
