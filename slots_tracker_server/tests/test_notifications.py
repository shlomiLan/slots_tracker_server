from unittest.mock import patch

import pytest

from slots_tracker_server.notifications import Notifications


@pytest.fixture(scope="module")
def connection():
    return Notifications()


def test_init_connection(connection):
    assert connection.db is not None


def test_init_connection_no_credentials():
    with patch('slots_tracker_server.notifications.initialize_app', return_value=None):
        with patch.dict('os.environ', {'FIREBASE_CREDENTIALS': ''}):
            with pytest.raises(KeyError):
                Notifications()

        with patch.dict('os.environ', {'FIREBASE_API_KEY': ''}):
            with pytest.raises(KeyError):
                Notifications()


def test_send_notifications(connection):
    assert connection.send('x', 'y', dry_run=True) is True
