# 3rd party modules
import pytest
from werkzeug.exceptions import NotFound, BadRequest
from bson.json_util import loads

from server.board import Board
from server.conf import Ids


# TODO: Chnage test to not use the real DB
def test_create_board():
    response = Board().create(dict(name='Stav3'))
    # We got a success code
    assert response[1] == 201


# TODO: after chaning DB add logic to test the contant
def test_read_all():
    assert Board.read_all() is not None


def test_read_one():
    new_board_id_as_str = str(loads(Board.read_one(id=Ids.VALID_BOARD_ID.value)).get('_id'))
    assert new_board_id_as_str == Ids.VALID_BOARD_ID.value


def test_read_one_invaild_id():
    # We got a error code
    with pytest.raises(BadRequest):
        Board.read_one(id=Ids.INVALID_BOARD_ID.value)


def test_read_one_id_not_in_db():
    # We got a error code
    with pytest.raises(NotFound):
        Board.read_one(id=Ids.NO_IN_DB_BOARD_ID.value)
