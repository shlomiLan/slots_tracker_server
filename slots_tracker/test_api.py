# system modules
import datetime

from slots_tracker.expense import create
from slots_tracker.conf import PayMethods


# TODO: Chnage test to not use the real DB
def test_create_new_expense():
    response = create(dict(amount=200, desc='Random stuff',
                           pay_method=PayMethods.Visa.value, timestamp=datetime.datetime.utcnow()))
    # We got a success code
    assert response[1] == 201
