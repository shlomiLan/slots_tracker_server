import mongoengine as db

from slots_tracker_server.db import BaseDocument


class PayMethods(BaseDocument):
    name = db.StringField(required=True, max_length=200, unique=True)
    active = db.BooleanField(default=True)


class Categories(BaseDocument):
    name = db.StringField(required=True, max_length=200, unique=True)
    active = db.BooleanField(default=True)


class Expense(BaseDocument):
    amount = db.FloatField(required=True)
    description = db.StringField(required=True, max_length=200, min_length=1)
    pay_method = db.ReferenceField(PayMethods, required=True)
    timestamp = db.DateTimeField(required=True)
    active = db.BooleanField(default=True)
    category = db.ReferenceField(Categories, required=True)
    one_time = db.BooleanField(default=False)

    @classmethod
    def fields(cls):
        return cls._fields

    @classmethod
    def get_all_reference_fields(cls):
        temp = []
        fields = cls.fields()
        for name, field in fields.items():
            field_class = type(field)
            if field_class == db.ReferenceField:
                temp.append((name, field.document_type))

        return temp
