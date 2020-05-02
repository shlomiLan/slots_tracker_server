import json

from slots_tracker_server.models import Categories
from slots_tracker_server.tests.conftest import login_user
from slots_tracker_server.utils import clean_api_object


def test_get_categories(client):
    headers, _ = login_user(client)
    rv = client.get('/categories/', headers=headers)
    r_data = json.loads(rv.get_data(as_text=True))
    assert isinstance(r_data, list)
    assert all(x.get('active') for x in r_data)
    instances = [x.get('instances') for x in r_data]
    assert sorted(instances, reverse=True) == instances


def test_get_category(client):
    headers, work_group_id = login_user(client)
    category = Categories.objects().filter(work_group=work_group_id)[0]
    rv = client.get('/categories/{}'.format(category.id), headers=headers)
    assert isinstance(json.loads(rv.get_data(as_text=True)), dict)


def test_get_deleted_category(client):
    headers, work_group_id = login_user(client)

    category = Categories(name='Very random text', active=False, work_group=work_group_id).save()
    rv = client.get('/categories/{}'.format(category.id), headers=headers)
    assert rv.status_code == 404


def test_post_category(client):
    headers, work_group_id = login_user(client)

    data = {'name': 'New visa'}
    expected_data = {'name': 'New visa', 'active': True, 'instances': 0, 'work_group': str(work_group_id)}

    rv = client.post('/categories/', json=data, headers=headers)
    result = json.loads(rv.get_data(as_text=True))
    # Clean the Expense
    clean_api_object(result)

    assert rv.status_code == 201
    assert result == expected_data


def test_post_duplicate_category(client):
    headers, work_group_id = login_user(client)

    data = {'name': 'New visa'}
    _ = client.post('/categories/', json=data, headers=headers)
    # Create another category with the same name
    rv = client.post('/categories/', json=data, headers=headers)
    assert rv.status_code == 400


def test_update_category(client):
    headers, work_group_id = login_user(client)
    category = Categories(name='Random category', work_group=work_group_id).save()
    category.name = '{}11111'.format(category.name)

    rv = client.put('/categories/{}'.format(category.id), json=category.to_json(), headers=headers)
    assert rv.status_code == 200


def test_update_duplicate_category(client):
    headers, work_group_id = login_user(client)

    name1 = 'Random random category'
    _ = Categories(name=name1, work_group=work_group_id).save()

    name2 = 'Random random random category'
    category = Categories(name=name2, work_group=work_group_id).save()

    category.name = name1
    rv = client.put('/categories/{}'.format(category.id), json=category.to_json(), headers=headers)
    assert rv.status_code == 400


def test_delete_category(client):
    headers, work_group_id = login_user(client)
    category = Categories(name='New category', work_group=work_group_id).save()
    rv = client.delete('/categories/{}'.format(category.id), headers=headers)
    assert rv.status_code == 200
    assert category.reload().active is False


def test_no_overlapping_categories(client):
    headers, _ = login_user(client)
    rv = client.get('/categories/', headers=headers)
    r_data = json.loads(rv.get_data(as_text=True))

    headers, _ = login_user(client, work_group_id=3)
    rv = client.get('/categories/', headers=headers)
    r_data_2 = json.loads(rv.get_data(as_text=True))

    assert all(x != y for x in r_data for y in r_data_2)
