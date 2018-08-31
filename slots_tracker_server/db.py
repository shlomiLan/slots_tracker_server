from bson import json_util
from flask import abort
from mongoengine import Document
from mongoengine.queryset import DoesNotExist, QuerySet

from slots_tracker_server.utils import find_and_convert_object_id, find_and_convert_date


class BaseQuerySet(QuerySet):
    """Mongoengine's queryset extended with handy extras."""

    def get_or_404(self, *args, **kwargs):
        """
        Get a document and raise a 404 Not Found error if it doesn't
        exist.
        """
        try:
            if 'active' not in kwargs:
                kwargs['active'] = True
            return self.get(*args, **kwargs)
        except DoesNotExist:
            abort(404)

    def to_json(self, *args, **kwargs):
        json_list = json_util.loads(super(BaseQuerySet, self).to_json())
        temp = []
        for json_obj in json_list:
            json_obj = find_and_convert_object_id(json_obj)
            temp.append(find_and_convert_date(json_obj))

        return temp


class BaseDocument(Document):
    meta = {'abstract': True, 'queryset_class': BaseQuerySet}

    def to_json(self):
        json_obj = json_util.loads(super(BaseDocument, self).to_json())
        json_obj = find_and_convert_object_id(json_obj)
        return find_and_convert_date(json_obj)
