from unittest import mock
import pytest

from slots_tracker_server.notifications import Notifications


@pytest.fixture(scope="module")
def connection():
    yield Notifications()


def test_init_connection(connection):
    assert connection.db is not None


def test_init_connection_no_credentials():
    with mock.patch.dict('os.environ', {'FIREBASE_CREDENTIALS': ''}):
        with pytest.raises(KeyError):
            Notifications(name='test1')

    with mock.patch.dict('os.environ', {'FIREBASE_API_KEY': ''}):
        with pytest.raises(KeyError):
            Notifications(name='test2')


def test_send_notifications(connection):
    assert connection.send('x', 'y', dry_run=True) == []
