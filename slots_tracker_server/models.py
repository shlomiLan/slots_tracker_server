import mongoengine as db
from mongoengine import DoesNotExist

from slots_tracker_server import app
from slots_tracker_server.db import BaseDocument


class PayMethods(BaseDocument):
    name = db.StringField(required=True, max_length=200, unique=True)
    active = db.BooleanField(default=True)
    instances = db.IntField(required=True, default=0)


class Categories(BaseDocument):
    name = db.StringField(required=True, max_length=200, unique=True)
    active = db.BooleanField(default=True)
    instances = db.IntField(required=True, default=0)
    added_by_user = db.BooleanField(default=True)
    parser_class = db.StringField(max_length=200)
    businesses = db.SortedListField(db.StringField(max_length=200))

    BUSINESS_IGNORE = ['colu', 'bit', 'box העברה באפליקציית', 'paypal', 'paybox']

    @staticmethod
    def is_business_name_in_list(values, business_name):
        return any(x in business_name for x in values) or any(x[::-1] in business_name for x in values)

    @classmethod
    def guess_new_category(cls, business_name):
        clean_business_name = business_name.replace('.', ' ').lower()
        if cls.is_business_name_in_list(cls.BUSINESS_IGNORE, clean_business_name):
            app.logger.info(f'business name: {business_name} is in ignore list')
            return None

        for category in cls.objects():
            if cls.is_business_name_in_list(category.businesses, clean_business_name):
                app.logger.info(f'business name: {business_name} is part of category: {category.name}')
                return category.name

        print(f'Can not find group for {clean_business_name}, creating new category')
        return False

    @classmethod
    def get_or_create_category_by_business_name(cls, business_name):
        is_new_category = False
        try:
            category = cls.objects.get(name=business_name)
        except DoesNotExist:
            category_name = cls.guess_new_category(business_name)

            if category_name is None:
                return False, is_new_category
            elif category_name is False:
                # Create new category
                category = cls(name=business_name, added_by_user=False).save()
                is_new_category = True
            else:
                # Find category by name
                category = cls.objects.get(name=category_name)

        return category, is_new_category

    def merge_categories(self, cat_to_merge_into_id):
        if self.added_by_user or self.added_by_user is None:
            raise Exception(f'Can not merge, {self.name} was added by user')

        cat_to_merge_into = Categories.objects.get(id=cat_to_merge_into_id)
        if not cat_to_merge_into.added_by_user:
            raise Exception(f'Can not merge, {cat_to_merge_into.name} was not added by user')

        Expense.objects.filter(category=self.id).update(multi=True, **{'category': cat_to_merge_into})
        cat_to_merge_into.businesses.append(self.name)
        cat_to_merge_into.save()
        self.delete()
        return f'Category {self.name} was merged with {cat_to_merge_into.name}'


class Expense(BaseDocument):
    amount = db.FloatField(required=True)
    pay_method = db.ReferenceField(PayMethods, required=True)
    timestamp = db.DateTimeField(required=True)
    active = db.BooleanField(default=True)
    category = db.ReferenceField(Categories, required=True)
    business_name = db.StringField(max_length=200)
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

    @classmethod
    def is_new_expense(cls, expense):
        res = cls.objects.filter(amount=expense.amount, timestamp=expense.timestamp, pay_method=expense.pay_method)
        return not bool(res)
