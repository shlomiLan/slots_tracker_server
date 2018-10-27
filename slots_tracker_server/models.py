import mongoengine as db

from slots_tracker_server.db import BaseDocument


class PayMethods(BaseDocument):
    name = db.StringField(required=True, max_length=200, unique=True)
    active = db.BooleanField(default=True)
    instances = db.IntField(required=True, default=0)


class Categories(BaseDocument):
    name = db.StringField(required=True, max_length=200, unique=True)
    active = db.BooleanField(default=True)
    instances = db.IntField(required=True, default=0)


class Expense(BaseDocument):
    amount = db.FloatField(required=True)
    description = db.StringField(required=True, max_length=200, min_length=1)
    pay_method = db.ReferenceField(PayMethods, required=True)
    timestamp = db.DateTimeField(required=True)
    active = db.BooleanField(default=True)
    category = db.ReferenceField(Categories, required=True)
    one_time = db.BooleanField(default=False)

    @classmethod
    def get_summary(cls):
        pass

    def save(self, **kwargs):
        self.update_reference_filed_count()
        return super(Expense, self).save(**kwargs)

    def update(self, **kwargs):
        for name, cls in self.get_all_reference_fields():
            ref_object = self.__getattribute__(name)
            if ref_object.id != kwargs.get(name):
                ref_object.instances -= 1
                ref_object.save()
                new_ref_object = cls.objects.get(id=kwargs.get(name))
                new_ref_object.instances += 1
                new_ref_object.save()

        return super(Expense, self).update(**kwargs)

    def update_reference_filed_count(self):
        for name, _ in self.get_all_reference_fields():
            ref_object = self.__getattribute__(name)
            ref_object.instances += 1

            ref_object.save()
