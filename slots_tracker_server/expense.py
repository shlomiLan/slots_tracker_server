import abc

import mongoengine_goodjson as gj
from bson import json_util, ObjectId
from flask import request
from flask.views import MethodView
from mongoengine.errors import NotUniqueError

from slots_tracker_server import db
from slots_tracker_server.utils import convert_to_object_id


class BaseAPI(MethodView):
    __metaclass__ = abc.ABCMeta

    @property
    @abc.abstractmethod
    def api_class(self):
        raise NotImplementedError

    def get(self, obj_id):
        if obj_id is None:
            return self.api_class.objects.to_json()
        else:
            object_id = convert_to_object_id(obj_id)
            instance = self.api_class.objects.get_or_404(id=object_id)
            return instance.to_json()

    def post(self, data):
        self.find_and_convert_ids(data)
        return self.api_class(**data).save().to_json(), 201

    def delete(self, obj_id):
        # TODO: add field in DB and mark object as deleted but don't really delete it
        return '', 200

    def put(self, obj_id, data):
        object_id = convert_to_object_id(obj_id)
        self.find_and_convert_ids(data)

        # Get and updated the expense
        instance = self.api_class.objects.get_or_404(id=object_id)
        instance.update(**data)
        #  Reload the expense with the updated data
        return instance.reload().to_json()

    @staticmethod
    def find_and_convert_ids(data):
        for k, v in data.items():
            if isinstance(v, dict):
                for k2, v2 in v.items():
                    if k2 == '$oid':
                        data[k] = convert_to_object_id(v2)


# Find way to add data with migration script
class PayMethods(db.Document, gj.Document):
    name = db.StringField(required=True, max_length=200, unique=True)


class PayMethodsAPI(BaseAPI):
    api_class = PayMethods

    def post(self, data=None):
        try:
            if not data:
                data = json_util.loads(request.data)
            return super(PayMethodsAPI, self).post(data)
        except NotUniqueError:
            return 'Name value must be unique', 400

    def put(self, obj_id, data=None):
        try:
            if not data:
                data = json_util.loads(request.data)
            return super(PayMethodsAPI, self).put(obj_id, data)
        except NotUniqueError:
            return 'Name value must be unique', 400


class Expense(db.Document, gj.Document):
    amount = db.IntField()
    description = db.StringField(required=True, max_length=200)
    pay_method = db.ReferenceField(PayMethods, required=True)
    timestamp = db.DateTimeField(required=True)
    # board = ReferenceField(Board, required=True)


class ExpenseAPI(BaseAPI):
    api_class = Expense

    def get(self, obj_id):
        data = json_util.loads(super(ExpenseAPI, self).get(obj_id))
        if isinstance(data, dict):
            data = [data]

        for item in data:
            pay_method_data = PayMethods.objects.get(id=item.get('pay_method')).to_json()
            item['pay_method'] = json_util.loads(pay_method_data)

        return json_util.dumps(data[0] if obj_id else data)

    def post(self, data=None):
        data = self.pay_method_json_to_object(data)
        return super(ExpenseAPI, self).post(data)

    def put(self, obj_id, data=None):
        data = self.pay_method_json_to_object(data)
        return super(ExpenseAPI, self).put(obj_id, data)

    @staticmethod
    def pay_method_json_to_object(data):
        if not data:
            data = json_util.loads(request.data)

        pay_method = data.get('pay_method')
        if pay_method and not isinstance(pay_method, ObjectId):
            pay_method_id = pay_method.get('_id') if isinstance(pay_method, dict) else pay_method
            data['pay_method'] = convert_to_object_id(pay_method_id)

        return data
