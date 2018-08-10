def test_home_page(client):
    rv = client.get('/')
    assert b'API index page' in rv.get_data()
