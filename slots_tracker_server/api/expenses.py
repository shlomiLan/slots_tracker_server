import copy

from bson import json_util
from flask import request

from slots_tracker_server.api.base import BasicObjectAPI, BaseAPI
from slots_tracker_server.models import Expense, PayMethods, Categories
from slots_tracker_server.utils import next_payment_date


class PayMethodsAPI(BasicObjectAPI):
    api_class = PayMethods


class CategoriesAPI(BasicObjectAPI):
    api_class = Categories


class ExpenseAPI(BaseAPI):
    api_class = Expense

    @staticmethod
    def get_full_doc(doc_id, docs):
        for doc in docs:
            if doc.get('_id') == doc_id:
                return doc

    def update_value_for_doc(self, field, docs):
        return self.get_full_doc(field, docs)

    def reference_fields_to_data(self, obj_data):
        for name, document_type in self.api_class.get_all_reference_fields():
            docs = document_type.objects.to_json()
            for entry in obj_data:
                entry[name] = self.update_value_for_doc(entry[name], docs)

    def get(self, obj_id):
        if obj_id:
            obj_data = super(ExpenseAPI, self).get(obj_id)
        else:
            obj_data = self.api_class.objects(active=True).order_by('one_time', '-timestamp').to_json()

        # Translate all reference fields from ID to data
        self.reference_fields_to_data(obj_data)

        return json_util.dumps(obj_data[0] if obj_id else obj_data)

    def post(self, obj_data=None):
        new_expenses_as_json = self.create_multi_expenses()
        return new_expenses_as_json, 201

    def put(self, obj_id, obj_data=None):
        new_expenses_as_json = self.create_multi_expenses(obj_id=obj_id)
        return new_expenses_as_json

    def create_multi_expenses(self, obj_id=None):
        obj_data = self.get_obj_data()
        self.reference_field_to_object_id(obj_data)

        new_expenses = []
        payments = int(request.args.get('payments', 1))
        payments_data = copy.deepcopy(obj_data)
        payments_data['amount'] = float(payments_data.get('amount')) / payments
        for i in range(payments):
            payments_data['timestamp'] = next_payment_date(obj_data['timestamp'], payment=i)
            new_expenses.append(self.create_doc(payments_data, obj_id))
        return json_util.dumps(new_expenses)
