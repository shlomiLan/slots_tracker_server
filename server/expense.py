# system modules
import datetime

# 3rd party modules
from flask.views import MethodView
from mongoengine import *

from server.base import Base
from server.board import Board


# Find way to add data with migration script
class PayMethods(Document):
    name = StringField(required=True, max_length=200)


class Expense(Base):
    amount = IntField()
    descreption = StringField(required=True, max_length=200)
    pay_method = ReferenceField(PayMethods, required=True)
    timestamp = DateTimeField(default=datetime.datetime.utcnow)
    board = ReferenceField(Board, required=True)


class ExpenseAPI(MethodView):
    def get(self, expense_id):
        if expense_id is None:
            # return a list of users
            return Expense.read_all()
        else:
            # expose a single user
            return Expense.read_one(id=expense_id)

    def post(self):
        # create a new user
        pass

    def delete(self, expense_id):
        # delete a single user
        pass

    def put(self, expense_id):
        # update a single user
        pass
