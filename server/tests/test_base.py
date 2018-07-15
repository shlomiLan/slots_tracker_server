def test_home_page(client):
    rv = client.get('/')
    assert b'Index Page3' in rv.get_data()
