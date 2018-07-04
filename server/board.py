# 3rd party modules
from mongoengine import *

from server.base import Base


class Board(Base):
    name = StringField(required=True, max_length=200)
