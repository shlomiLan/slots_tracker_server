from datetime import datetime

import pytest

from slots_tracker_server import app as flask_app
from slots_tracker_server.models import Expense, PayMethods, Categories, Users, WorkGroups


basic_collections = [PayMethods, Categories, Users]
all_collections = basic_collections + [Expense, WorkGroups]


def clean_db():
    for collection in all_collections:
        collection.objects.delete()


def add_fake_data(work_group_object):
    for collection in basic_collections:
        for i in range(3):
            new_obj_name = f'{collection._meta["collection"]}_{i}'
            if collection == Users:
                collection(email=new_obj_name, password=f'password_{i}', work_group=work_group_object).save()
            else:
                collection(name=new_obj_name, work_group=work_group_object).save()


@pytest.fixture(scope="session", autouse=True)
def client():
    flask_client = flask_app.test_client()

    # Clean the DB
    clean_db()

    # create work groups
    for i in range(2):
        WorkGroups(name=f'work_group_{i}').save()

    # create fake documents
    work_group = WorkGroups.objects().first()
    add_fake_data(work_group)

    now_date = datetime.utcnow
    expense_data = dict(amount=200, pay_method=PayMethods.objects().first().id, timestamp=now_date,
                        category=Categories.objects().first().id, work_group=work_group)
    Expense(**expense_data).save()

    # Create deleted items
    expense_data['active'] = False
    Expense(**expense_data).save()

    yield flask_client

    # Clean the DB
    clean_db()
