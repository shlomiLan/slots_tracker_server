from unittest import mock

import pytest
from python_http_client import UnauthorizedError

import slots_tracker_server.email as email


@mock.patch('slots_tracker_server.email.send_email', return_value={'status_code': 202})
def test_send_email(_, client):
    res = email.send_email(content='This is test content', subject='Test subject')
    assert res.get('status_code') == 202


def test_no_api_key():
    with mock.patch.dict('os.environ', {'SENDGRID_API_KEY': ''}):
        with pytest.raises(UnauthorizedError):
            email.send_email(content='This is test content', subject='Test subject')
