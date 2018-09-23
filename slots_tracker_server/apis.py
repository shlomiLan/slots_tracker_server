import abc

from bson import json_util, ObjectId
from flask import request
from flask.views import MethodView
from mongoengine import DateTimeField, BooleanField
from mongoengine.errors import NotUniqueError

from slots_tracker_server.gsheet import write_expense
from slots_tracker_server.models import Expense, PayMethods, Categories
from slots_tracker_server.utils import convert_to_object_id, clean_api_object


class BaseAPI(MethodView):
    __metaclass__ = abc.ABCMeta

    @property
    @abc.abstractmethod
    def api_class(self):
        raise NotImplementedError

    def get(self, obj_id):
        if obj_id is None:
            if hasattr(self.api_class, 'timestamp') and type(self.api_class.timestamp) == DateTimeField and \
                    hasattr(self.api_class, 'one_time') and type(self.api_class.one_time) == BooleanField:
                return self.api_class.objects(active=True).order_by('one_time', '-timestamp').to_json()

            if hasattr(self.api_class, 'name'):
                return self.api_class.objects(active=True).order_by('name').to_json()

            return self.api_class.objects(active=True).to_json()
        else:
            object_id = convert_to_object_id(obj_id)
            instance = self.api_class.objects.get_or_404(id=object_id)
            return instance.to_json()

    def post(self, obj_data):
        # TODO: Check that all reference fields are not inactive before creating a new object
        return self.api_class(**obj_data).save()

    def delete(self, obj_id):
        instance = self.api_class.objects.get_or_404(id=obj_id)
        instance.active = False
        instance.save()
        return '', 200

    def put(self, obj_id, obj_data):
        clean_api_object(obj_data)
        object_id = convert_to_object_id(obj_id)

        # Get and updated the expense
        instance = self.api_class.objects.get_or_404(id=object_id)
        instance.update(**obj_data)
        #  Reload the expense with the updated object
        new_expense_as_json = instance.reload().to_json()
        self.convert_object_id_json(new_expense_as_json)
        return json_util.dumps(new_expense_as_json)

    @staticmethod
    def get_obj_data():
        return json_util.loads(request.data)
        # return obj_data


class BasicObjectAPI(BaseAPI):
    __metaclass__ = abc.ABCMeta

    @property
    @abc.abstractmethod
    def api_class(self):
        raise NotImplementedError

    def get(self, obj_id):
        obj_data = super(BasicObjectAPI, self).get(obj_id)
        if isinstance(obj_data, dict):
            obj_data = [obj_data]

        return json_util.dumps(obj_data[0] if obj_id else obj_data)

    def post(self, obj_data=None):
        obj_data = self.get_obj_data()
        try:
            return json_util.dumps(super(BasicObjectAPI, self).post(obj_data).to_json()), 201
        except NotUniqueError:
            return 'Name value must be unique', 400

    def put(self, obj_id, obj_data=None):
        obj_data = self.get_obj_data()
        try:
            return super(BasicObjectAPI, self).put(obj_id, obj_data)
        except NotUniqueError:
            return 'Name value must be unique', 400


class PayMethodsAPI(BasicObjectAPI):
    api_class = PayMethods


class CategoriesAPI(BasicObjectAPI):
    api_class = Categories


class ExpenseAPI(BaseAPI):
    api_class = Expense

    def get(self, obj_id):
        obj_data = super(ExpenseAPI, self).get(obj_id)
        if isinstance(obj_data, dict):
            obj_data = [obj_data]

        for name, document_type in self.api_class.get_all_reference_fields():
            for item in obj_data:
                item[name] = document_type.objects.get(id=item.get(name)).to_json()

        limit = int(request.args.get('limit')) if request.args.get('limit') else len(obj_data)
        return json_util.dumps(obj_data[0] if obj_id else obj_data[:limit])

    def post(self, obj_data=None):
        obj_data = self.get_obj_data()
        self.convert_reference_field_data_to_object_id(obj_data)
        new_expense = super(ExpenseAPI, self).post(obj_data)
        new_expense_as_json = new_expense.to_json()
        self.convert_object_id_json(new_expense_as_json)

        write_expense(new_expense)
        return json_util.dumps(new_expense_as_json), 201

    def put(self, obj_id, obj_data=None):
        obj_data = self.get_obj_data()
        self.convert_reference_field_data_to_object_id(obj_data)
        return super(ExpenseAPI, self).put(obj_id, obj_data)

    def convert_reference_field_data_to_object_id(self, obj_data):
        for name, _ in self.api_class.get_all_reference_fields():
            field_data = obj_data.get(name)
            if field_data and not isinstance(field_data, ObjectId):
                field_data_id = field_data.get('_id') if isinstance(field_data, dict) else field_data
                obj_data[name] = convert_to_object_id(field_data_id)

    def convert_object_id_json(self, obj_data):
        for name, document_type in self.api_class.get_all_reference_fields():
            field_id = obj_data.get(name)
            field_data_as_json = document_type.objects.get(id=field_id).to_json()
            obj_data[name] = field_data_as_json
