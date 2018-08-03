import click


@click.command()
def write_gsheet():
    from slots_tracker_server.gsheet import write_expense
    print('ehre')
    write_expense(dict(action='XXX', category='YYY', date='CCCC', amount=100000, pay_method='Visa'))
