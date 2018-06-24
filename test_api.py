import pytest

from expense import create_new_expense
from conf import PayMethods


def test_create_new_expense():
    response = create_new_expense(amount=200, desc='Random stuff', pay_method=PayMethods.Visa)
    assert response.get('code') == 201
