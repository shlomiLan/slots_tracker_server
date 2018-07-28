from bson import json_util
from flask import abort
from mongoengine import Document
from mongoengine.queryset import DoesNotExist, QuerySet

from slots_tracker_server.utils import object_id_to_str, convert_date


class BaseQuerySet(QuerySet):
    """Mongoengine's queryset extended with handy extras."""

    def get_or_404(self, *args, **kwargs):
        """
        Get a document and raise a 404 Not Found error if it doesn't
        exist.
        """
        try:
            return self.get(*args, **kwargs)
        except DoesNotExist:
            abort(404)

    def first_or_404(self):
        """Same as get_or_404, but uses .first, not .get."""
        obj = self.first()
        if obj is None:
            abort(404)

        return obj

    def to_json(self, *args, **kwargs):
        json_list = json_util.loads(super(BaseQuerySet, self).to_json())
        temp = []
        for json_obj in json_list:
            json_obj = object_id_to_str(json_obj)
            temp.append(convert_date(json_obj))

        return json_util.dumps(temp)


class BaseDocument(Document):
    meta = {'abstract': True, 'queryset_class': BaseQuerySet}

    def to_json(self):
        json_obj = json_util.loads(super(BaseDocument, self).to_json())
        json_obj = object_id_to_str(json_obj)
        return json_util.dumps(convert_date(json_obj))
