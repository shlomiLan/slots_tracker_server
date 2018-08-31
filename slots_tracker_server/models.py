from mongoengine import *

from slots_tracker_server.db import BaseDocument


class PayMethods(BaseDocument):
    name = StringField(required=True, max_length=200, unique=True)


class Expense(BaseDocument):
    amount = IntField(required=True)
    description = StringField(required=True, max_length=200)
    pay_method = ReferenceField(PayMethods, required=True)
    timestamp = DateTimeField(required=True)
