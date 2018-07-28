# # system modules
# import json
#
# # 3rd party modules
# from flask.views import MethodView
# from flask import request
# from mongoengine import *
#
#
# class Board(Document):
#     name = StringField(required=True, max_length=200)
#
#
# class BoardAPI(MethodView):
#     def get(self, board_id):
#         if board_id is None:
#             return Board.objects.to_json()
#         else:
#             object_id = convert_to_object_id(board_id)
#             try:
#                 # Does the board exist in the DB
#                 return Board.objects.get(id=object_id).to_json()
#             except DoesNotExist:
#                 abort(404, 'Board with id {} not found'.format(object_id))
#
#     def post(self):
#         board_data = json.loads(request.data)
#         return Expense(board_data).save().to_json, 201
#
#     def delete(self, board_id):
#         # delete a single user
#         pass
#
#     def put(self, board_id):
#         # update a single user
#         pass
