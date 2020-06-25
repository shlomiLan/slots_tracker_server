from slots_tracker_server.models import Expense, PayMethods, Categories
from slots_tracker_server.tests.test_utils import DEFAULT_DATE_NEW_OBJECT


def test_new_expenses():
    expense = Expense(amount=200, timestamp=DEFAULT_DATE_NEW_OBJECT, pay_method=PayMethods.objects().first())

    assert Expense.is_new_expense(expense)

    # Save expense
    expense.category = Categories.objects().first()
    expense.save()
    assert not Expense.is_new_expense(expense)
