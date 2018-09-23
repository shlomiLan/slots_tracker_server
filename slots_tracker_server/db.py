from bson import json_util
from flask import abort
from mongoengine import Document, ReferenceField
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
            find_and_convert_object_id(json_obj)
            find_and_convert_date(json_obj)
            temp.append(json_obj)

        return temp


class BaseDocument(Document):
    _fields = None
    meta = {'abstract': True, 'queryset_class': BaseQuerySet}

    def to_json(self):
        json_obj = json_util.loads(super(BaseDocument, self).to_json())
        find_and_convert_object_id(json_obj)
        find_and_convert_date(json_obj)

        return json_obj

    @classmethod
    def fields(cls):
        return cls._fields

    @classmethod
    def get_all_reference_fields(cls):
        temp = []
        fields = cls.fields()
        for name, field in fields.items():
            field_class = type(field)
            if field_class == ReferenceField:
                temp.append((name, field.document_type))

        return temp
