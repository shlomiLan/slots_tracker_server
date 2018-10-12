from bson import json_util

from slots_tracker_server.api.base import BasicObjectAPI, BaseAPI
from slots_tracker_server.models import Withdrawal, Kinds


class KindsAPI(BasicObjectAPI):
    api_class = Kinds


class WithdrawalAPI(BaseAPI):
    api_class = Withdrawal

    def get(self, obj_id):
        if obj_id:
            obj_data = super(WithdrawalAPI, self).get(obj_id)
        else:
            obj_data = self.api_class.objects(active=True).order_by('-timestamp').to_json()

        # Move to external function
        for name, document_type in self.api_class.get_all_reference_fields():
            for item in obj_data:
                item[name] = document_type.objects.get(id=item.get(name)).to_json()

        return json_util.dumps(obj_data[0] if obj_id else obj_data)

    def post(self, obj_data=None):
        new_withdrawals_as_json = self.create_multi_withdrawals()
        return new_withdrawals_as_json, 201

    def put(self, obj_id, obj_data=None):
        new_withdrawals_as_json = self.create_multi_withdrawals(obj_id=obj_id)
        return new_withdrawals_as_json

    def create_multi_withdrawals(self, obj_id=None):
        obj_data = self.get_obj_data()
        self.reference_field_to_object_id(obj_data)

        return json_util.dumps([self.create_doc(obj_data, obj_id)])
