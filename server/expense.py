# system modules
import json
import datetime

# 3rd party modules
from flask.views import MethodView
from flask import request

from server import db

from server.board import Board
from server.utils import convert_to_object_id


# Find way to add data with migration script
class PayMethods(db.Document):
    name = db.StringField(required=True, max_length=200)


class Expense(db.Document):
    amount = db.IntField()
    descreption = db.StringField(required=True, max_length=200)
    # pay_method = ReferenceField(PayMethods, required=True)
    # timestamp = DateTimeField(default=datetime.datetime.utcnow)
    # board = ReferenceField(Board, required=True)


class ExpenseAPI(MethodView):
    def get(self, expense_id):
        if expense_id is None:
            return Expense.objects.to_json()
        else:
            object_id = convert_to_object_id(expense_id)
            expense = Expense.objects.get_or_404(id=object_id)

            return expense.to_json()

    def post(self):
        expense_data = json.loads(request.data)
        return Expense(**expense_data).save().to_json(), 201

    def delete(self, expense_id):
        # delete a single user
        pass

    def put(self, expense_id):
        object_id = convert_to_object_id(expense_id)
        expense_data = json.loads(request.data)
        # Get and updaete the expense
        expense = Expense.objects.get_or_404(id=object_id)
        expense.update(**expense_data)
        #  Reload the expense with the updated data
        return expense.reload().to_json()
