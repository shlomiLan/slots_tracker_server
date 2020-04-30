import json
from datetime import datetime

import pytest

from slots_tracker_server import app as flask_app
from slots_tracker_server.models import Expense, PayMethods, Categories, Users, WorkGroups


BASIC_COLLECTIONS = [PayMethods, Categories, Users]
ALL_COLLECTIONS = BASIC_COLLECTIONS + [Expense, WorkGroups]
EMAIL_PATTERN = 'users_{user_id}_work_group_{work_group_id}'
WORK_GROUP_PATTERN = 'work_group_{id}'
AMOUNT = 200


def clean_db():
    for collection in ALL_COLLECTIONS:
        collection.objects.delete()


def add_fake_data():
    for i, work_group in enumerate(WorkGroups.objects.all()):
        # Work group without any objects
        if i == 0:
            continue

        for collection in BASIC_COLLECTIONS:
            collection_name = collection._meta["collection"]
            # Work group with users but no other objects
            if i == 1 and collection != Users:
                continue

            for j in range(3):
                new_obj_name = f'{collection_name}_{j}_{work_group.name}'
                if collection == Users:
                    collection(email=new_obj_name, password=f'password_{j}', work_group=work_group).save()
                else:
                    collection(name=new_obj_name, work_group=work_group).save()

        if i not in (0, 1):
            now_date = datetime.utcnow
            expense_data = dict(amount=AMOUNT, pay_method=PayMethods.objects().first().id, timestamp=now_date,
                                category=Categories.objects().first().id, work_group=work_group)
            Expense(**expense_data).save()

            # Create deleted items
            expense_data['active'] = False
            Expense(**expense_data).save()


@pytest.fixture(scope="session", autouse=True)
def client():
    flask_client = flask_app.test_client()

    # Clean the DB
    clean_db()

    # create work groups
    for i in range(4):
        WorkGroups(name=WORK_GROUP_PATTERN.format(id=i)).save()

    # create fake documents
    add_fake_data()

    yield flask_client

    # Clean the DB
    clean_db()


def get_user_email(user_id, work_group_id):
    return EMAIL_PATTERN.format(user_id=user_id, work_group_id=work_group_id)


def login_user(client, user_id=0, work_group_id=2):
    work_group = WorkGroups.objects.get(name=WORK_GROUP_PATTERN.format(id=work_group_id))
    user_email = get_user_email(user_id, work_group_id)
    res = client.post('/login/', json={'email': user_email,
                                       'password': f'password_{user_id}'})
    access_token = json.loads(res.get_data(as_text=True))['access_token']

    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    return headers, work_group.id
