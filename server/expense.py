# system modules
import json
import datetime

# 3rd party modules
from flask.views import MethodView
from flask import request
from mongoengine import *
from mongoengine.errors import NotUniqueError

from server.db import BaseDocument
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
        self.find_and_convert_ids(data)
        return self.api_class(**data).save().to_json(), 201

    def delete(self, id):
        # delete a single user
        pass

    def put(self, id):
        object_id = convert_to_object_id(id)
        data = json.loads(request.data)
        self.find_and_convert_ids(data)

        # Get and updaete the expense
        instance = self.api_class.objects.get_or_404(id=object_id)
        instance.update(**data)
        #  Reload the expense with the updated data
        return instance.reload().to_json()

    def find_and_convert_ids(self, data):
        for k, v in data.items():
            if isinstance(v, dict):
                for k2, v2 in v.items():
                    if k2 == '$oid':
                        data[k] = convert_to_object_id(v2)


# Find way to add data with migration script
class PayMethods(BaseDocument):
    name = StringField(required=True, max_length=200, unique=True)


class PayMethodsAPI(BaseAPI):
    api_class = PayMethods

    def post(self):
        try:
            return super(PayMethodsAPI, self).post()
        except NotUniqueError:
            return 'Name value must be unique', 400

    def put(self, id):
        try:
            return super(PayMethodsAPI, self).put(id)
        except NotUniqueError:
            return 'Name value must be unique', 400


class Expense(BaseDocument):
    amount = IntField()
    descreption = StringField(required=True, max_length=200)
    pay_method = ReferenceField(PayMethods, required=True)
    # timestamp = DateTimeField(default=datetime.datetime.utcnow)
    # board = ReferenceField(Board, required=True)


class ExpenseAPI(BaseAPI):
    api_class = Expense
