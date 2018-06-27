import datetime


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
