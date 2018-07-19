# system modules
import json
import datetime

# 3rd party modules
from flask.views import MethodView
from flask import request

from server import db

from server.board import Board
from server.utils import convert_to_object_id


class BaseAPI(MethodView):
    def get(self, id):
        if id is None:
            return self.api_class.objects.to_json()
        else:
            object_id = convert_to_object_id(id)
            instance = self.api_class.objects.get_or_404(id=object_id)

            return instance.to_json()

    def post(self):
        data = json.loads(request.data)
        return self.api_class(**data).save().to_json(), 201

    def delete(self, id):
        # delete a single user
        pass

    def put(self, id):
        object_id = convert_to_object_id(id)
        data = json.loads(request.data)
        # Get and updaete the expense
        instance = self.api_class.objects.get_or_404(id=object_id)
        instance.update(**data)
        #  Reload the expense with the updated data
        return self.api_class.reload().to_json()


# Find way to add data with migration script
class PayMethods(db.Document):
    name = db.StringField(required=True, max_length=200)


class PayMethodsAPI(BaseAPI):
    api_class = PayMethods


class Expense(db.Document):
    amount = db.IntField()
    descreption = db.StringField(required=True, max_length=200)
    pay_method = db.ReferenceField(PayMethods, required=True)
    # timestamp = DateTimeField(default=datetime.datetime.utcnow)
    # board = ReferenceField(Board, required=True)


class ExpenseAPI(BaseAPI):
    api_class = Expense
