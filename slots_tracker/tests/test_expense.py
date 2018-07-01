# stsyem modules
import datetime

from slots_tracker.expense import Expense, PayMethods


# TODO: Chnage test to not use the real DB
def test_create_expense():
    response = Expense().create(dict(amount=200, descreption='Random stuff',
                                     pay_method=PayMethods.objects()[0],
                                     timestamp=datetime.datetime.utcnow))
    # We got a success code
    assert response[1] == 201


def test_create_expense_no_date():
    response = Expense().create(dict(amount=200, descreption='Random stuff',
                                     pay_method=PayMethods.objects()[0]))
    # We got a success code
    assert response[1] == 201
    assert 'timestamp' in response[0]
