# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
import os
from itertools import chain

from invoke import task
from progress.bar import Bar

from pyinvoke.base import init_app
from pyinvoke.utils import transform_expense_to_dict, translate, reference_objects_str_to_id, clean_doc_data, BASEDIR, \
    BACKUPS, run, load_yaml_from_file


@task()
def clean_db(c, settings=None):
    init_app(c, settings=settings)
    clean_expenses(c)
    clean_pay_methods(c)
    clean_categories(c)


@task(init_app)
def clean_expenses(_):
    # Leave here tp prevent circular import
    from slots_tracker_server.models import Expense

    print('Removing all expense objects')
    Expense.objects.delete()


@task(init_app)
def clean_pay_methods(_):
    # Leave here tp prevent circular import
    from slots_tracker_server.models import PayMethods

    print('Removing all pay methods objects')
    PayMethods.objects.delete()


@task(init_app)
def clean_categories(_):
    # Leave here tp prevent circular import
    from slots_tracker_server.models import Categories

    print('Removing all categories objects')
    Categories.objects.delete()


@task()
def init_db(c, env=None, settings=None):
    init_app(c, env, settings)
    clean_db(c, settings)
    initial_data = load_yaml_from_file(os.path.join(BASEDIR, 'resources', 'init_db.yml'))
    # Leave here tp prevent circular import
    from slots_tracker_server.models import PayMethods, Categories
    insert_db_data(PayMethods, initial_data.get('pay_methods'))
    insert_db_data(Categories, initial_data.get('categories'))


def insert_db_data(cls, db_data):
    print('Creating {}'.format(cls.__name__))

    for item in db_data:
        cls(name=item).save()


@task()
def add_count_to_ref_fields(c, settings=None):
    init_app(c, settings=settings)
    from slots_tracker_server.models import Expense

    # TODO: Change this so it will make changes based on chain(PayMethods.objects(), Categories.objects()
    # Now we repeat this process to many times
    # expenses = Expense.objects()
    # for expense in Bar('Resting').iter(expenses):
    #     pass
    # expense.update_reference_filed_count(reset=True)

    expenses = Expense.objects()
    for expense in Bar('Updating').iter(expenses):
        expense.update_reference_filed_count()


def get_db_info():
    # Use get to not get error when loading the 'dev' settings
    return os.environ['DB_HOST'], os.environ['DB_PORT'], os.environ['DB_NAME'], os.environ.get('DB_USERNAME'), \
           os.environ.get('DB_PASS')


@task()
def remove_numbers_from_name(c, settings=None):
    init_app(c, settings=settings)

    from slots_tracker_server.models import Categories, PayMethods
    for item in Bar('Updating').iter(chain(PayMethods.objects(), Categories.objects())):
        item_name = item.name
        if item_name[0].isdigit():
            item_name = item_name.split(' ')
            item_name = ' '.join(item_name[1:])
            item.name = item_name
            item.save()


# Users
@task()
def list_users(c, settings=None):
    init_app(c, settings=settings)
    from slots_tracker_server.models import Users
    users = Users.objects()
    print('Loading users')
    for user in users:
        print(user.to_json())


@task()
def add_user(c, email, password, group, settings=None):
    init_app(c, settings=settings)
    from slots_tracker_server.models import Users, WorkGroups
    work_group = WorkGroups.objects.get(name=group)
    print(Users(email=email, password=password, work_group=work_group).save())
    list_users(c)


@task()
def list_objects(c, settings=None, cls=None):
    init_app(c, settings=settings)
    from slots_tracker_server.models import WorkGroups, Categories
    if cls == 'categories':
        objects = Categories.objects()
    else:
        objects = WorkGroups.objects()
    print(f'Loading {cls}')
    for o in objects:
        print(o.to_json())


# WorkGroup
@task()
def add_group(c, group_name, settings=None):
    init_app(c, settings=settings)
    from slots_tracker_server.models import WorkGroups
    print(WorkGroups(name=group_name).save())


@task()
def add_group_to_objects(c, group_name, settings=None):
    init_app(c, settings=settings)
    from slots_tracker_server.models import WorkGroups, Categories, PayMethods, Expense
    workgroup = WorkGroups.objects.get(name=group_name)
    for collection in [Categories, PayMethods, Expense]:
        print(f'Adding workgroup: {workgroup} to collection" {collection}')
        for obj in collection.objects():
            print(obj)
            obj.work_group = workgroup
            obj.save()
        pass
