import click
from bson import json_util


# Google spreadsheet
@click.command()
def write_expense_to_gsheet():
    # Leave here to prevent circular import
    from slots_tracker_server.gsheet import write_expense
    from slots_tracker_server.expense import Expense
    expense = Expense.objects[0]
    expense_as_json = json_util.loads(expense.to_json())
    expense_as_json['pay_method'] = expense.pay_method.name
    expense_as_json['category'] = 'XXX'
    write_expense(expense_as_json)


@click.command()
def update_gsheet_header():
    from slots_tracker_server.gsheet import get_worksheet, get_headers
    wks = get_worksheet()
    headers = get_headers(wks)
    new_headers = ['_id', 'description', 'category', 'timestamp', 'amount', 'pay_method']

    for i, header in enumerate(headers):
        headers[i].value = new_headers[i]

    wks.update_cells(headers)
