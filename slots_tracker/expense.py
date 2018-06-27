import datetime

from db import mongo_client


def expense_data_from_url_parameters(parameters):
    amount = parameters.get('amount')
    desc = parameters.get('desc')
    pay_method = parameters.get('pay_method')
    date = parameters.get('date', datetime.datetime.today())

    return amount, desc, pay_method, date


def create_new_expense(db, amount, desc, pay_method, date):
    expense = dict(amount=amount, desc=desc, pay_method=pay_method, date=date)
    expense_id = db.expenses.insert_one(expense).inserted_id

    return dict(code=201) if expense_id else dict(code=400)


def create_expense():
    # TODO: find better way to do that
    # amount, desc, pay_method, date = expense_data_from_url_parameters(request.args)
    # create_new_expense(mongo_client, amount, desc, pay_method, date)
    return 'Expense Page post'


def read():
    # expenses_q = mongo_client.expenses.find({'amount': 200})
    return 'Expense Page get'
