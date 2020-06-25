import json
from slots_tracker_server.charts import NUM_OF_CHARTS


# Charts
def test_get_charts(client):
    rv = client.get('/charts/')
    r_data = json.loads(rv.get_data(as_text=True))
    assert isinstance(r_data, list)
    assert len(r_data) == NUM_OF_CHARTS
