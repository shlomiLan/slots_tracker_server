import json

from slots_tracker_server.models import PayMethods
from slots_tracker_server.tests.conftest import login_user
from slots_tracker_server.utils import clean_api_object


def test_get_pay_methods(client):
    headers, _ = login_user(client)
    rv = client.get('/pay_methods/', headers=headers)
    r_data = json.loads(rv.get_data(as_text=True))
    assert isinstance(r_data, list)
    assert all(x.get('active') for x in r_data)
    instances = [x.get('instances') for x in r_data]
    assert sorted(instances, reverse=True) == instances


def test_get_pay_method(client):
    headers, work_group_id = login_user(client)
    pay_method = PayMethods.objects().filter(work_group=work_group_id)[0]
    rv = client.get('/pay_methods/{}'.format(pay_method.id), headers=headers)
    assert isinstance(json.loads(rv.get_data(as_text=True)), dict)


def test_get_deleted_pay_method(client):
    headers, work_group_id = login_user(client)

    pay_method = PayMethods(name='Very random text', active=False, work_group=work_group_id).save()
    rv = client.get('/pay_methods/{}'.format(pay_method.id), headers=headers)
    assert rv.status_code == 404


def test_post_pay_method(client):
    headers, work_group_id = login_user(client)

    data = {'name': 'New visa', 'work_group': str(work_group_id)}
    expected_data = {'name': 'New visa', 'active': True, 'instances': 0, 'work_group': str(work_group_id)}

    rv = client.post('/pay_methods/', json=data, headers=headers)
    result = json.loads(rv.get_data(as_text=True))
    # Clean the Expense
    clean_api_object(result)

    assert rv.status_code == 201
    assert result == expected_data


def test_post_duplicate_pay_method(client):
    headers, work_group_id = login_user(client)

    data = {'name': 'New visa', 'work_group': str(work_group_id)}
    _ = client.post('/pay_methods/', json=data, headers=headers)
    # Create another pay method with the same name
    rv = client.post('/pay_methods/', json=data, headers=headers)
    assert rv.status_code == 400


def test_update_pay_method(client):
    headers, work_group_id = login_user(client)
    pay_method = PayMethods(name='Random pay method', work_group=work_group_id).save()
    pay_method.name = '{}11111'.format(pay_method.name)

    rv = client.put('/pay_methods/{}'.format(pay_method.id), json=pay_method.to_json(), headers=headers)
    assert rv.status_code == 200


def test_update_duplicate_pay_method(client):
    headers, work_group_id = login_user(client)

    name1 = 'Random random pay method'
    _ = PayMethods(name=name1, work_group=work_group_id).save()

    name2 = 'Random random random pay method'
    pay_method = PayMethods(name=name2, work_group=work_group_id).save()

    pay_method.name = name1
    rv = client.put('/pay_methods/{}'.format(pay_method.id), json=pay_method.to_json(), headers=headers)
    assert rv.status_code == 400


def test_delete_pay_method(client):
    headers, work_group_id = login_user(client)
    pay_method = PayMethods(name='New pay method', work_group=work_group_id).save()
    rv = client.delete('/pay_methods/{}'.format(pay_method.id), headers=headers)
    assert rv.status_code == 200
    assert pay_method.reload().active is False


def test_no_overlapping_pay_methods(client):
    headers, _ = login_user(client)
    rv = client.get('/pay_methods/', headers=headers)
    r_data = json.loads(rv.get_data(as_text=True))

    headers, _ = login_user(client, work_group_id=3)
    rv = client.get('/pay_methods/', headers=headers)
    r_data_2 = json.loads(rv.get_data(as_text=True))

    assert all(x != y for x in r_data for y in r_data_2)
