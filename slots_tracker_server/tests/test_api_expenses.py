from datetime import datetime
import json

from slots_tracker_server.api.expenses import ExpenseAPI
from slots_tracker_server.models import Expense, PayMethods, Categories, WorkGroups
from slots_tracker_server.tests.conftest import login_user, AMOUNT
from slots_tracker_server.utils import clean_api_object


NEW_AMOUNT = 100
WORK_GROUP_KEY = 'work_group'


def test_get_expenses(client):
    headers, work_group_id = login_user(client)
    rv = client.get('/expenses/', headers=headers)
    r_data = json.loads(rv.get_data(as_text=True))
    assert isinstance(r_data, list)
    assert all(x.get('active') for x in r_data)
    for name, document_type in ExpenseAPI.api_class.get_all_reference_fields():
        assert all(isinstance(x[name], dict) for x in r_data)

    assert all(x[WORK_GROUP_KEY]['_id'] == str(work_group_id) for x in r_data)


def test_no_overlapping_expenses(client):
    headers, _ = login_user(client)
    rv = client.get('/expenses/', headers=headers)
    r_data = json.loads(rv.get_data(as_text=True))

    headers, _ = login_user(client, work_group_id=3)
    rv = client.get('/expenses/', headers=headers)
    r_data_2 = json.loads(rv.get_data(as_text=True))

    assert all(x != y for x in r_data for y in r_data_2)


def test_get_expense(client):
    headers, work_group_id = login_user(client)
    expense = Expense.objects.filter(work_group=work_group_id)[0]
    rv = client.get('/expenses/{}'.format(expense.id), headers=headers)
    assert isinstance(json.loads(rv.get_data(as_text=True))[0], dict)


def test_no_access_to_other_user_expense(client):
    _, work_group_id = login_user(client, work_group_id=3)
    expense = Expense.objects.filter(work_group=work_group_id)[0]

    # Login as user from different work group
    headers, _ = login_user(client)
    rv = client.get('/expenses/{}'.format(expense.id), headers=headers)
    assert rv.status_code == 404


def test_get_expense_empty_result(client):
    _, work_group_id = login_user(client, work_group_id=1)
    expense = Expense.objects.filter(work_group=work_group_id)
    assert not expense


def test_filtered_expenses(client):
    headers, _ = login_user(client)
    rv = client.get('/expenses/?filter={}'.format(AMOUNT), headers=headers)
    data = json.loads(rv.get_data(as_text=True))
    assert isinstance(data[0], dict)
    assert len(data) == 1


def test_get_deleted_expense(client):
    headers, work_group_id = login_user(client)
    expense = Expense(amount=AMOUNT, pay_method=PayMethods.objects().first(),
                      timestamp=datetime.utcnow(), active=False, category=Categories.objects().first(),
                      work_group=work_group_id).save()
    rv = client.get('/expenses/{}'.format(expense.id), headers=headers)
    assert rv.status_code == 404


def test_get_expense_404(client):
    invalid_id = '5b6d42132c8884b302632182'
    headers, _ = login_user(client)
    rv = client.get('/expenses/{}'.format(invalid_id), headers=headers)
    assert rv.status_code == 404


# @given(amount=st.floats(min_value=-10000, max_value=10000),
#        timestamp=st.datetimes(min_value=datetime(1900, 1, 1, 0, 0)), active=st.booleans(),
#        one_time=st.booleans(), payments=st.integers(2, 10))
# @settings(deadline=None)
# def test_post_expenses(client, amount, timestamp, active, one_time, payments):
#     pay_method = PayMethods.objects().first()
#     category = Categories.objects().first()
#
#     data = {'amount': amount, 'pay_method': pay_method.to_json(), 'timestamp': timestamp,
#             'category': category.to_json(), 'active': active, 'one_time': one_time}
#
#     rv = client.post(f'/expenses/?payments={payments}', json=data)
#     result = json.loads(rv.get_data(as_text=True))
#     assert len(result) == payments
#     assert rv.status_code == 201
#
#     for i, r in enumerate(result):
#         # Clean the Expense
#         clean_api_object(r)
#         data['pay_method']['instances'] += 1
#         data['category']['instances'] += 1
#         expected_data = {'amount': ExpenseAPI.calc_amount(amount, payments), 'pay_method': data['pay_method'],
#                          'timestamp': date_to_str(next_payment_date(date_to_str(timestamp), payment=i)),
#                          'active': active, 'category': data['category'], 'one_time': one_time}
#         assert r == expected_data
#

def test_delete_expense(client):
    headers, work_group_id = login_user(client)
    expense = Expense(amount=AMOUNT, pay_method=PayMethods.objects().first(),
                      timestamp=datetime.utcnow(), category=Categories.objects().first(),
                      work_group=work_group_id).save()
    rv = client.delete('/expenses/{}'.format(expense.id), headers=headers)
    assert rv.status_code == 200


def test_update_expense(client):
    headers, work_group_id = login_user(client)
    pay_method = PayMethods.objects().filter(work_group=work_group_id)[0]
    category = Categories.objects().filter(work_group=work_group_id)[0]
    work_group = WorkGroups.objects().get(id=work_group_id)

    amount, timestamp, active, one_time = expense_data()
    data = {'amount': amount, 'pay_method': pay_method.to_json(), 'timestamp': timestamp,
            'category': category.to_json(), 'active': active, 'one_time': one_time, 'work_group': work_group.to_json()}

    rv = client.post('/expenses/', json=data, headers=headers)
    result = json.loads(rv.get_data(as_text=True))
    assert len(result) == 1
    result = result[0]
    result['amount'] = NEW_AMOUNT
    obj_id = result.get('_id')
    clean_api_object(result)

    rv = client.put('/expenses/{}'.format(obj_id), json=result, headers=headers)
    result = json.loads(rv.get_data(as_text=True))
    assert len(result) == 1
    result = result[0]

    # reload pay method and category
    pay_method = pay_method.reload()
    category = category.reload()

    assert rv.status_code == 200
    assert result.get('amount') == NEW_AMOUNT
    # Increase because of the post
    assert data.get('pay_method').get('instances') + 1 == pay_method.instances
    assert data.get('category').get('instances') + 1 == category.instances


def test_update_expense_change_ref_filed(client):
    headers, work_group_id = login_user(client)
    pay_method = PayMethods.objects().filter(work_group=work_group_id)[0]
    category = Categories.objects().filter(work_group=work_group_id)[0]
    work_group = WorkGroups.objects().get(id=work_group_id)

    amount, timestamp, active, one_time = expense_data()
    data = {'amount': amount, 'pay_method': pay_method.to_json(), 'timestamp': timestamp,
            'category': category.to_json(), 'active': active, 'one_time': one_time, 'work_group': work_group.to_json()}

    rv = client.post('/expenses/', json=data, headers=headers)
    result = json.loads(rv.get_data(as_text=True))
    assert len(result) == 1
    result = result[0]
    old_pay_method = pay_method.to_json()

    new_pay_method = PayMethods(name='Very random text 1111', work_group=work_group_id).save()
    result['pay_method'] = new_pay_method.to_json()
    obj_id = result.get('_id')
    clean_api_object(result)

    rv = client.put('/expenses/{}'.format(obj_id), json=result, headers=headers)
    _ = json.loads(rv.get_data(as_text=True))

    # reload pay method and category
    pay_method = pay_method.reload()
    new_pay_method = new_pay_method.reload()
    category = category.reload()

    assert rv.status_code == 200
    assert new_pay_method.instances == 1
    # Increase because of the post
    assert old_pay_method.get('instances') == pay_method.instances
    assert data.get('category').get('instances') + 1 == category.instances


def test_calc_amount():
    assert ExpenseAPI.calc_amount(100, 3) == 33.333333333333336
    assert ExpenseAPI.calc_amount(62, 4) == 15.5
    assert ExpenseAPI.calc_amount(63, 5) == 12.6


def test_post_expenses_with_payments(client):
    amount, timestamp, active, one_time = expense_data()
    headers, work_group_id = login_user(client)
    pay_method = PayMethods.objects().filter(work_group=work_group_id)[0]
    category = Categories.objects().filter(work_group=work_group_id)[0]
    work_group = WorkGroups.objects().get(id=work_group_id)

    data = {'amount': amount, 'pay_method': pay_method.to_json(), 'timestamp': timestamp,
            'category': category.to_json(), 'active': active, 'one_time': one_time, 'work_group': work_group.to_json()}

    payments = 3
    rv = client.post(f'/expenses/?payments={payments}', json=data, headers=headers)
    result = json.loads(rv.get_data(as_text=True))

    assert rv.status_code == 201
    assert isinstance(result, list)
    assert len(result) == payments


def expense_data():
    return AMOUNT, datetime.utcnow(), True, False
