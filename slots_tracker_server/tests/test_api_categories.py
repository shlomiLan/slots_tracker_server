from datetime import datetime
import json

from slots_tracker_server.api.expenses import ExpenseAPI
from slots_tracker_server.models import Expense, PayMethods, Categories
from slots_tracker_server.utils import clean_api_object


def test_get_categories(client):
    rv = client.get('/categories/')
    r_data = json.loads(rv.get_data(as_text=True))
    assert isinstance(r_data, list)
    assert all(x.get('active') for x in r_data)


def test_get_user_added_categories(client):
    rv = client.get('/categories/?added_by_user=true')
    r_data = json.loads(rv.get_data(as_text=True))
    assert isinstance(r_data, list)
    assert all(x.get('active') for x in r_data)


def test_get_not_user_added_categories(client):
    rv = client.get('/categories/?added_by_user=false')
    r_data = json.loads(rv.get_data(as_text=True))
    assert isinstance(r_data, list)
    assert all(x.get('active') for x in r_data)


def test_no_category_is_user_added_and_not_user_added(client):
    rv = client.get('/categories/?added_by_user=true')
    user_added_categories = json.loads(rv.get_data(as_text=True))

    rv = client.get('/categories/?added_by_user=false')
    not_user_added_categories = json.loads(rv.get_data(as_text=True))
    pairs = zip(user_added_categories, not_user_added_categories)
    assert all(x != y for x, y in pairs)


def test_get_category(client):
    category = Categories.objects[0]
    rv = client.get('/categories/{}'.format(category.id))
    assert isinstance(json.loads(rv.get_data(as_text=True)), dict)


def test_post_category(client):
    cat_name = 'New cat'
    data = {'name': cat_name}
    expected_data = {'name': cat_name, 'active': True, 'instances': 0, 'added_by_user': True, 'businesses': []}

    rv = client.post('/categories/', json=data)
    result = json.loads(rv.get_data(as_text=True))
    # Clean the Category
    clean_api_object(result)

    assert rv.status_code == 201
    assert result == expected_data


def test_post_category_not_added_by_user(client):
    cat_name = 'New cat'
    data = {'name': cat_name, 'added_by_user': False}
    expected_data = {'name': cat_name, 'active': True, 'instances': 0, 'added_by_user': False, 'businesses': []}

    rv = client.post('/categories/', json=data)
    result = json.loads(rv.get_data(as_text=True))
    # Clean the Category
    clean_api_object(result)

    assert rv.status_code == 201
    assert result == expected_data
