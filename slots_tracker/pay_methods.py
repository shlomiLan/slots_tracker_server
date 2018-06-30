from mongoengine import *


connect('slots_tracker')


# Find way to add data with migration script
class PayMethods(Document):
    name = StringField(required=True, max_length=200)
