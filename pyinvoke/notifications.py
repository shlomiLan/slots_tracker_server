from invoke import task

from pyinvoke.base import init_app


@task(init_app)
def send_monthly_update(_):
    from slots_tracker_server.charts import Charts
    from slots_tracker_server.notifications import Notifications

    table = Charts().get_summary_table()
    if table and table.get('data'):
        message = ''
        for row in table.get('data'):
            message += f'{row[0]}: {row[1]}\n'

        Notifications().send('Monthly update', message)
