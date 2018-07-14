# stsyem modules
import datetime

from server.expense import Expense, PayMethods
from server.board import Board


# TODO: Chnage test to not use the real DB
def test_create_expense():
    response = Expense(amount=200, descreption='Random stuff')
    # pay_method=PayMethods.objects()[0], timestamp=datetime.datetime.utcnow, board=Board.objects()[0])

    # We got a new object
    assert response is not None
