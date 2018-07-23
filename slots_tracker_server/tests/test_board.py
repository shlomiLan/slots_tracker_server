# # 3rd party modules
# import pytest
# from werkzeug.exceptions import NotFound, BadRequest
# from bson.json_util import loads
#
# from server.board import Board, BoardAPI
# from server.conf import Ids
#
#
# import os
# import tempfile
#
# import pytest
# from mongoengine import *
#
# from server import app


# # TODO: Chnage test to not use the real DB
# def test_create_board():
#     response = Board(name='New board')
#     # We got a success code
#     assert response is not None
#
#
# def test_read_one(client):
#     print(client.get('/'))
#     # board = Board.objects()[0]
#     # print(BoardAPI.get(board, board_id=Ids.VALID_BOARD_ID.value))
#     # new_board_id_as_str = str(loads(Board.get(id=Ids.VALID_BOARD_ID.value)).get('_id'))
#     # assert new_board_id_as_str == Ids.VALID_BOARD_ID.value
#
#
# def test_read_one_invaild_id():
#     # We got a error code
#     with pytest.raises(BadRequest):
#         Board.read_one(id=Ids.INVALID_BOARD_ID.value)
#
#
# def test_read_one_id_not_in_db():
#     # We got a error code
#     with pytest.raises(NotFound):
#         Board.read_one(id=Ids.NO_IN_DB_BOARD_ID.value)
