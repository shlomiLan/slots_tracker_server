# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
import os
from itertools import chain

from invoke import task
from progress.bar import Bar

from pyinvoke.base import init_app
from pyinvoke.email import email
from pyinvoke.utils import BASEDIR, BACKUPS, run, load_yaml_from_file


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
    return os.environ['DB_HOST'], os.environ['DB_NAME'], os.environ.get('DB_USERNAME'), \
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


@task()
def backup_db(c, settings='prod', force_restore=False):
    init_app(c, settings=settings)
    host, port, db_name, username, password = get_db_info()
    today_str = str(datetime.datetime.now().date()).replace('-', '_')
    dest_path = os.path.join(BACKUPS, today_str)
    run(c, f'mongodump -h {host}:{port} -d {db_name} -u {username} -p {password} -o {dest_path}', False)

    day = datetime.datetime.now().day
    # If first backup of the month or force
    if day <= 7 or force_restore:
        res = restore_db(c, today_str)
        if res and res.exited != 0:
            email_text = res.stderr
        else:
            email_text = f'The {today_str} daily backup was restored to stage successfully.'

        email(c, subject='DB restore test', content=email_text)


@task()
def restore_db(c, date, backup_db_name='slots_tracker', settings='dev'):
    if settings == 'prod':
        raise Exception('Manually remove this line to restore to prod DB?')

    init_app(c, settings=settings, force=True)
    host, db_name, username, password = get_db_info()
    source_path = os.path.join(BACKUPS, date, backup_db_name)
    if settings == 'dev':
        run(c, f'mongorestore -h {host} -d {db_name} {source_path} --drop', False)
    else:
        run(c, f'mongorestore -h {host} -d {db_name} -u {username} -p {password} {source_path} --drop', False)


@task()
def bus_to_cat_data_to_db(c, settings='dev'):
    init_app(c, settings=settings)

    from slots_tracker_server.models import Categories

    category_to_business_name = {
        'Transportation': ["באבאל", "gett"],
        'Eating out': ["eatmeat", "ג'ירף", "קונדיטוריה", "קפה", 'בייקרי', 'מאפה נאמן', 'רולדין', 'לנדוור', 'נונה',
                       'שולי לוצי', 'הכובשים', 'בוטיק סנטרל', 'לחם ושות', 'gin club', 'ארומה'],
        'Car': ["חניון", "דור - יקום-צמרת", 'דלק', 'מנטה', 'סונול', 'רכב חובה', 'פנגו', 'דואלי מכונות אוטומטיות', 'ביטוח רכב'],
        'Groceries': ["אי אם פי אם", 'am pm', 'pm am', 'am:pm', 'גרציאני', 'מרקטו', 'מלכה מרקט אקספרס', 'יינות ביתן',
                      'שופרסל', 'טיב טעם',
                      'מגה בעיר', 'שוקיט', 'ויקטורי', 'פירות', 'יוכי אספרגוס'],
        'Communication': ['פלאפון חשבון תקופתי', 'קיי אס פי', 'spotify', 'zagg', 'hot', 'הוט נט'],
        'Home': ['מקס סטוק', 'חברת חשמל לישראל', 'חברת החשמל לישראל', 'netflix', 'עתיקות אוחיון', 'שטראוס מים בע"מ',
                 'סולתם', 'הום סנטר'],
        'Shows': ['רב חן'],
        'Health': ['קרן מכבי'],
        'Insurance': ['הסתדרות העובדים הכלל'],
        'Super-Pharm': ['סופר פארם'],
        'Gifts': ['kiwico'],
        'Baby': ['יופיי ליגת לה לצה'],
        'Sport': ['סטודיו טשרנחובסקי', 'כפיים שיווק וקידום מכירות']
    }

    for cat_name, businesses in category_to_business_name.items():
        category = Categories.objects.get(name=cat_name)
        for business in businesses:
            if business not in category.businesses:
                category.businesses.append(business)

        category.save()
