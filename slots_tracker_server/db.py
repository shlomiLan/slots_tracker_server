import mongoengine_goodjson as gj
from bson import json_util
from flask_mongoengine import BaseQuerySet

from slots_tracker_server import db
from slots_tracker_server.utils import convert_date


class QuerySet(BaseQuerySet):
    def to_json(self, *args, **kwargs):
        json_list = json_util.loads(super(QuerySet, self).to_json())
        temp = []
        for json_obj in json_list:
            temp.append(convert_date(json_obj))

        return json_util.dumps(temp)


class BaseDocument(db.Document, gj.Document):
    meta = {'abstract': True, 'queryset_class': QuerySet}

    def to_json(self):
        json_obj = json_util.loads(super(BaseDocument, self).to_json())
        return json_util.dumps(convert_date(json_obj))
