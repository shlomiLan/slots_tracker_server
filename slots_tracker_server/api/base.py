import abc

from bson import json_util, ObjectId
from flask import request
from flask.views import MethodView
from mongoengine import NotUniqueError

from slots_tracker_server.gsheet import write_expense, update_expense
from slots_tracker_server.utils import convert_to_object_id, clean_api_object


class BaseAPI(MethodView):
    __metaclass__ = abc.ABCMeta

    @property
    @abc.abstractmethod
    def api_class(self):
        raise NotImplementedError

    def get(self, obj_id):
        object_id = convert_to_object_id(obj_id)
        instance = self.api_class.objects.get_or_404(id=object_id)
        return [instance.to_json()]

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

        # Get and updated the object
        instance = self.api_class.objects.get_or_404(id=object_id)
        instance.update(**obj_data)
        return instance.reload()

    @staticmethod
    def get_obj_data():
        return json_util.loads(request.data)

    def objects_id_to_json(self, obj_data):
        for name, document_type in self.api_class.get_all_reference_fields():
            field_id = obj_data.get(name)
            field_data_as_json = document_type.objects.get(id=field_id).to_json()
            obj_data[name] = field_data_as_json

    def reference_field_to_object_id(self, obj_data):
        for name, _ in self.api_class.get_all_reference_fields():
            field_data = obj_data.get(name)
            if field_data and not isinstance(field_data, ObjectId):
                field_data_id = field_data.get('_id') if isinstance(field_data, dict) else field_data
                obj_data[name] = convert_to_object_id(field_data_id)

    def create_doc(self, obj_data, obj_id=None):
        if obj_id:
            new_doc = BaseAPI.put(self, obj_id, obj_data)
        else:
            new_doc = BaseAPI.post(self, obj_data)
        new_doc_as_json = new_doc.to_json()
        self.objects_id_to_json(new_doc_as_json)

        if obj_id:
            update_expense(new_doc)
        else:
            write_expense(new_doc)

        return new_doc_as_json


class BasicObjectAPI(BaseAPI):
    __metaclass__ = abc.ABCMeta

    @property
    @abc.abstractmethod
    def api_class(self):
        raise NotImplementedError

    def get(self, obj_id):
        if obj_id:
            obj_data = super(BasicObjectAPI, self).get(obj_id)
        else:
            obj_data = self.api_class.objects(active=True).order_by('-instances').to_json()

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
            new_expense_as_json = super(BasicObjectAPI, self).put(obj_id, obj_data).to_json()
            self.objects_id_to_json(new_expense_as_json)
            return json_util.dumps(new_expense_as_json)
        except NotUniqueError:
            return 'Name value must be unique', 400
