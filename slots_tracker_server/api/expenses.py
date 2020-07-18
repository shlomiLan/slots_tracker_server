import copy

from bson import json_util
from flask import request
from mongoengine import Q

from slots_tracker_server.api.base import BasicObjectAPI, BaseAPI
from slots_tracker_server.models import Expense, PayMethods, Categories
from slots_tracker_server.utils import next_payment_date


class PayMethodsAPI(BasicObjectAPI):
    api_class = PayMethods


class CategoriesAPI(BasicObjectAPI):
    api_class = Categories


class ExpenseAPI(BaseAPI):
    api_class = Expense

    def __init__(self):
        self.docs = dict()
        for name, document_type in self.api_class.get_all_reference_fields():
            self.docs[name] = document_type.objects.to_json()

    @staticmethod
    def get_full_doc_by_id(doc_id, docs):
        # return filter(lambda x: x.get('_id') == doc_id, docs)

        for doc in docs:
            if doc.get('_id') == doc_id:
                return doc

    def update_value_for_doc(self, field, docs):
        return self.get_full_doc_by_id(field, docs)

    def reference_fields_to_data(self, obj_data):
        for name, _ in self.api_class.get_all_reference_fields():
            for entry in obj_data:
                entry[name] = self.update_value_for_doc(entry[name], self.docs[name])

    def get_filters(self):
        conditions = Q(active=True)

        filter_keywords = ['amount', 'pay_method', 'category', 'timestamp']
        for keyword in filter_keywords:
            filter_data = request.args.get(keyword)
            if filter_data:
                conditions = conditions & Q(**{keyword: filter_data})

        return conditions

    def get(self, obj_id):
        filters = self.get_filters()
        filtered_objs = self.api_class.objects(active=True)
        if obj_id:
            filtered_objs = super(ExpenseAPI, self).get(obj_id)
        else:
            if filters:
                filtered_objs = filtered_objs.filter(filters)

            filtered_objs = filtered_objs.limit(50).order_by('one_time', '-timestamp').to_json()
        # Translate all reference fields from ID to data
        self.reference_fields_to_data(filtered_objs)

        return json_util.dumps(filtered_objs)

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
        payments_data['amount'] = self.calc_amount(payments_data.get('amount'), payments)
        for i in range(payments):
            payments_data['timestamp'] = next_payment_date(obj_data['timestamp'], payment=i)
            new_expenses.append(self.create_doc(payments_data, obj_id))
        return json_util.dumps(new_expenses)

    @staticmethod
    def calc_amount(original_amount, payments):
        return float(original_amount) / payments
