# Monthly update
def test_get_monthly_update(client):
    rv = client.get('/monthly_update/')
    r_data = rv.get_data(as_text=True)
    assert r_data == 'Message sent'
