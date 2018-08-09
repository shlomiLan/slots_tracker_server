import click
from bson import json_util


@click.command()
def write_gsheet():
    # Leave here to prevent circular import
    from slots_tracker_server.gsheet import write_expense
    from slots_tracker_server.expense import Expense
    expense = Expense.objects[0]
    expense_as_json = json_util.loads(expense.to_json())
    expense_as_json['pay_method'] = expense.pay_method.name
    expense_as_json['category'] = 'XXX'
    write_expense(expense_as_json)
