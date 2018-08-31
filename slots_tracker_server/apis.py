import abc

from bson import json_util, ObjectId
from flask import request
from flask.views import MethodView
from mongoengine.errors import NotUniqueError

from slots_tracker_server.models import Expense, PayMethods
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

    def post(self, obj_data):
        return json_util.dumps(self.api_class(**obj_data).save().to_json()), 201

    def delete(self, obj_id):
        # TODO: add field in DB and mark object as deleted but don't really delete it
        return '', 200

    def put(self, obj_id, obj_data):
        # Remove the object ID from obj_data
        del obj_data['_id']
        object_id = convert_to_object_id(obj_id)

        # Get and updated the expense
        instance = self.api_class.objects.get_or_404(id=object_id)
        instance.update(**obj_data)
        #  Reload the expense with the updated object
        return json_util.dumps(instance.reload().to_json())


class PayMethodsAPI(BaseAPI):
    api_class = PayMethods

    def post(self, obj_data=None):
        try:
            obj_data = self.get_obj_data(obj_data)
            return super(PayMethodsAPI, self).post(obj_data)
        except NotUniqueError:
            return 'Name value must be unique', 400

    def put(self, obj_id, obj_data=None):
        try:
            obj_data = self.get_obj_data(obj_data)
            return super(PayMethodsAPI, self).put(obj_id, obj_data)
        except NotUniqueError:
            return 'Name value must be unique', 400


class ExpenseAPI(BaseAPI):
    api_class = Expense

    def get(self, obj_id):
        obj_data = super(ExpenseAPI, self).get(obj_id)
        if isinstance(obj_data, dict):
            obj_data = [obj_data]

        for item in obj_data:
            pay_method_data = PayMethods.objects.get(id=item.get('pay_method')).to_json()
            item['pay_method'] = pay_method_data

        return json_util.dumps(obj_data[0] if obj_id else obj_data)

    def post(self, obj_data=None):
        obj_data = self.get_obj_data(obj_data)
        self.pay_method_json_to_object(obj_data)
        return super(ExpenseAPI, self).post(obj_data)

    def put(self, obj_id, obj_data=None):
        obj_data = self.get_obj_data(obj_data)
        self.pay_method_json_to_object(obj_data)
        return super(ExpenseAPI, self).put(obj_id, obj_data)

    @staticmethod
    def pay_method_json_to_object(obj_data):
        pay_method = obj_data.get('pay_method')
        if pay_method and not isinstance(pay_method, ObjectId):
            pay_method_id = pay_method.get('_id') if isinstance(pay_method, dict) else pay_method
            obj_data['pay_method'] = convert_to_object_id(pay_method_id)

    @staticmethod
    def get_obj_data(obj_data):
        if not obj_data:
            return json_util.loads(request.data)
        return obj_data
