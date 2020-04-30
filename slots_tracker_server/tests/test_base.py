from slots_tracker_server.tests.conftest import login_user

PAGE_TEXT = b'API index page'


def test_home_page_without_login(client):
    rv = client.get('/')
    assert PAGE_TEXT in rv.get_data()


def test_home_page_with_login(client):
    headers, _ = login_user(client)
    rv = client.get('/', headers=headers)
    assert PAGE_TEXT in rv.get_data()
