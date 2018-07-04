# 3rd party modules
from flask import abort
from mongoengine import *

from server.utils import convert_to_object_id


class Base(Document):
    meta = {'allow_inheritance': True, 'abstract': True}

    @classmethod
    def create(cls, object):
        new_item = cls(**object).save()

        return cls.read_one(id=new_item.id), 201

    @classmethod
    def read_all(cls):
        return cls.objects.to_json()

    @classmethod
    @convert_to_object_id
    def read_one(cls, id=None):
        """
        This function responds to a request for /api/{cls}/{board_id}
        with one matching class item from its list
        :param id: id of the class item to find
        :return:   class item with matching id
        """
        try:
            # Does the expense exist in the DB
            return cls.objects.get(id=id).to_json()
        except DoesNotExist:
            abort(404, '{} with id {} not found'.format(cls.__name__, id))
