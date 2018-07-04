# system modules
import datetime

# 3rd party modules
from mongoengine import *

from server.base import Base
from server.board import Board


# Find way to add data with migration script
class PayMethods(Document):
    name = StringField(required=True, max_length=200)


class Expense(Base):
    amount = IntField()
    descreption = StringField(required=True, max_length=200)
    pay_method = ReferenceField(PayMethods, required=True)
    timestamp = DateTimeField(default=datetime.datetime.utcnow)
    board = ReferenceField(Board, required=True)
