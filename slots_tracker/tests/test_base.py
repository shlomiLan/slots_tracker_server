# 3rd party modules
import pytest
from unittest.mock import Mock
from werkzeug.exceptions import BadRequest

from slots_tracker.base import Base
from slots_tracker.utils import convert_to_object_id
from slots_tracker.conf import Ids


def test_convert_to_object_id_valid():
    func = Mock()
    dec = convert_to_object_id(func)
    assert isinstance(dec(Base, id=Ids.VALID_BOARD_ID.value), Mock)


def test_convert_to_object_id_invalid():
    func = Mock()
    dec = convert_to_object_id(func)
    with pytest.raises(BadRequest):
        dec(Base, id=Ids.INVALID_BOARD_ID.value)
