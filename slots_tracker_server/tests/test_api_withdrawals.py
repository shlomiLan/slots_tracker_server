import datetime
import json
from unittest import mock

import hypothesis.strategies as st
from hypothesis import given

from slots_tracker_server.models import PayMethods, Withdrawal, Kinds
from slots_tracker_server.utils import date_to_str, clean_api_object


# Withdrawals
def test_get_withdrawals(client):
    rv = client.get('/withdrawals/')
    r_data = json.loads(rv.get_data(as_text=True))
    assert isinstance(r_data, list)
    assert all(x.get('active') for x in r_data)


def test_get_withdrawal(client):
    withdrawal = Withdrawal.objects[0]
    rv = client.get('/withdrawals/{}'.format(withdrawal.id))
    assert isinstance(json.loads(rv.get_data(as_text=True)), dict)


def test_get_deleted_withdrawals(client):
    withdrawal = Withdrawal(amount=200, pay_method=PayMethods.objects().first(), timestamp=datetime.datetime.utcnow(),
                            active=False, kind=Kinds.objects().first()).save()
    rv = client.get('/withdrawals/{}'.format(withdrawal.id))
    assert rv.status_code == 404


def test_get_withdrawal_404(client):
    invalid_id = '5b6d42132c8884b302632182'
    rv = client.get('/withdrawals/{}'.format(invalid_id))
    assert rv.status_code == 404


@mock.patch('slots_tracker_server.api.base.gsheet.write_doc', return_value='None')
@given(amount=st.floats(min_value=-1000000000, max_value=1000000000),
       timestamp=st.datetimes(min_value=datetime.datetime(1900, 1, 1, 0, 0)), active=st.booleans(), )
def test_post_withdrawals(_, client, amount, timestamp, active):
    pay_method = PayMethods.objects().first()
    kind = Kinds.objects().first()

    data = {'amount': amount, 'pay_method': pay_method.to_json(), 'timestamp': timestamp, 'kind': kind.to_json(),
            'active': active}

    rv = client.post('/withdrawals/', json=data)
    result = json.loads(rv.get_data(as_text=True))
    assert len(result) == 1
    result = result[0]
    # Clean the withdrawal
    clean_api_object(result)

    # reload pay method and kind
    pay_method = pay_method.reload()
    kind = kind.reload()

    expected_data = {'amount': amount, 'pay_method': pay_method.to_json(), 'timestamp': date_to_str(timestamp),
                     'active': active, 'kind': kind.to_json()}

    assert rv.status_code == 201
    assert result == expected_data


def test_delete_withdrawal(client):
    withdrawal = Withdrawal(amount=200, pay_method=PayMethods.objects().first(), timestamp=datetime.datetime.utcnow(),
                            kind=Kinds.objects().first()).save()
    rv = client.delete('/withdrawals/{}'.format(withdrawal.id))
    assert rv.status_code == 200


def test_update_withdrawal(client):
    pay_method = PayMethods.objects().first()
    kind = Kinds.objects().first()

    amount, timestamp, active = test_withdrawal_data()
    data = {'amount': amount, 'pay_method': pay_method.to_json(), 'timestamp': timestamp, 'kind': kind.to_json(),
            'active': active}

    rv = client.post('/withdrawals/', json=data)
    result = json.loads(rv.get_data(as_text=True))
    assert len(result) == 1
    result = result[0]
    result['amount'] = 100
    obj_id = result.get('_id')
    clean_api_object(result)

    rv = client.put('/withdrawals/{}'.format(obj_id), json=result)
    result = json.loads(rv.get_data(as_text=True))
    assert len(result) == 1
    result = result[0]

    # reload pay method
    pay_method = pay_method.reload()

    assert rv.status_code == 200
    assert result.get('amount') == 100
    # Increase because of the post
    assert data.get('pay_method').get('instances') + 1 == pay_method.instances


def test_update_withdrawal_change_ref_filed(client):
    pay_method = PayMethods.objects().first()
    kind = Kinds.objects().first()

    amount, timestamp, active = test_withdrawal_data()
    data = {'amount': amount, 'pay_method': pay_method.to_json(), 'timestamp': timestamp, 'kind': kind.to_json(),
            'active': active}

    rv = client.post('/withdrawals/', json=data)
    result = json.loads(rv.get_data(as_text=True))
    assert len(result) == 1
    result = result[0]
    old_pay_method = pay_method.to_json()

    new_pay_method = PayMethods(name='Very random text 1111').save()
    result['pay_method'] = new_pay_method.to_json()
    obj_id = result.get('_id')
    clean_api_object(result)

    rv = client.put('/expenses/{}'.format(obj_id), json=result)
    _ = json.loads(rv.get_data(as_text=True))

    # reload pay methods
    pay_method = pay_method.reload()
    new_pay_method = new_pay_method.reload()

    assert rv.status_code == 200
    assert new_pay_method.instances == 0
    # Instances counter should not change
    assert old_pay_method.get('instances') == pay_method.instances


def test_withdrawal_data():
    return 100, datetime.datetime.utcnow(), True
