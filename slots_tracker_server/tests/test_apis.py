import datetime
import json

import hypothesis.strategies as st
from hypothesis import given

from slots_tracker_server.models import Expense, PayMethods, Categories
from slots_tracker_server.utils import object_id_to_str, date_to_str, clean_api_object


# Expense
def test_get_expenses(client):
    rv = client.get('/expenses/')
    r_data = json.loads(rv.get_data(as_text=True))
    assert isinstance(r_data, list)
    assert all(x.get('active') for x in r_data)


def test_get_expense(client):
    expense = Expense.objects[0]
    rv = client.get('/expenses/{}'.format(expense.id))
    assert isinstance(json.loads(rv.get_data(as_text=True)), dict)


def test_get_deleted_expense(client):
    expense = Expense(amount=200, description='Random stuff', pay_method=PayMethods.objects().first(),
                      timestamp=datetime.datetime.utcnow(), active=False, category=Categories.objects().first()).save()
    rv = client.get('/expenses/{}'.format(expense.id))
    assert rv.status_code == 404


def test_get_expense_404(client):
    invalid_id = '5b6d42132c8884b302632182'
    rv = client.get('/expenses/{}'.format(invalid_id))
    assert rv.status_code == 404


@given(amount=st.integers(min_value=-1000000000, max_value=1000000000), description=st.text(),
       timestamp=st.datetimes(min_value=datetime.datetime(1900, 1, 1, 0, 0)), active=st.booleans())
def test_post_expenses(client, amount, description, timestamp, active):
    pay_method = PayMethods.objects().first()
    category = Categories.objects().first()
    data = {'amount': amount, 'description': description, 'pay_method': pay_method.to_json(), 'timestamp': timestamp,
            'category': category.to_json(), 'active': active}
    expected_data = {'amount': amount, 'description': description, 'pay_method': object_id_to_str(pay_method.id),
                     'timestamp': date_to_str(timestamp), 'active': active, 'category': object_id_to_str(category.id)}

    rv = client.post('/expenses/', json=data)
    result = json.loads(rv.get_data(as_text=True))
    # Clean the Expense
    clean_api_object(result)

    assert rv.status_code == 201
    assert result == expected_data


def test_delete_expense(client):
    expense = Expense(amount=200, description='Random stuff', pay_method=PayMethods.objects().first(),
                      timestamp=datetime.datetime.utcnow(), category=Categories.objects().first()).save()
    rv = client.delete('/expenses/{}'.format(expense.id))
    assert rv.status_code == 200


def test_update_expense(client):
    expense = Expense(amount=200, description='Random stuff', pay_method=PayMethods.objects().first(),
                      timestamp=datetime.datetime.utcnow(), category=Categories.objects().first()).save()
    expense.amount = 100
    rv = client.put('/expenses/{}'.format(expense.id), json=expense.to_json())
    assert rv.status_code == 200


# Pay method
def test_get_pay_methods(client):
    rv = client.get('/pay_methods/')
    r_data = json.loads(rv.get_data(as_text=True))
    assert isinstance(r_data, list)
    assert all(x.get('active') for x in r_data)


def test_get_pay_method(client):
    pay_method = PayMethods.objects[0]
    rv = client.get('/pay_methods/{}'.format(pay_method.id))
    assert isinstance(json.loads(rv.get_data(as_text=True)), dict)


def test_get_deleted_pay_method(client):
    pay_method = PayMethods(name='Very random text', active=False).save()
    rv = client.get('/pay_methods/{}'.format(pay_method.id))
    assert rv.status_code == 404


def test_post_pay_method(client):
    data = {'name': 'New visa'}
    expected_data = {'name': 'New visa', 'active': True}

    rv = client.post('/pay_methods/', json=data)
    result = json.loads(rv.get_data(as_text=True))
    # Clean the Expense
    clean_api_object(result)

    assert rv.status_code == 201
    assert result == expected_data


def test_post_duplicate_pay_method(client):
    data = {'name': 'New visa'}
    _ = client.post('/pay_methods/', json=data)
    # Create another pay method with the same name
    rv = client.post('/pay_methods/', json=data)
    assert rv.status_code == 400


def test_update_pay_method(client):
    pay_method = PayMethods('Random pay method').save()
    pay_method.name = '{}11111'.format(pay_method.name)

    rv = client.put('/pay_methods/{}'.format(pay_method.id), json=pay_method.to_json())
    assert rv.status_code == 200


def test_update_duplicate_pay_method(client):
    name1 = 'Random random pay method'
    _ = PayMethods(name1).save()

    name2 = 'Random random random pay method'
    pay_method = PayMethods(name2).save()

    pay_method.name = name1
    rv = client.put('/pay_methods/{}'.format(pay_method.id), json=pay_method.to_json())
    assert rv.status_code == 400


def test_delete_pay_method(client):
    pay_method = PayMethods('New pay method').save()
    rv = client.delete('/pay_methods/{}'.format(pay_method.id))
    assert rv.status_code == 200
    assert pay_method.reload().active is False
