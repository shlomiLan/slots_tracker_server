import requests
from invoke import task

from pyinvoke.base import init_app


@task(init_app)
def send_monthly_update(_, target_env='production'):
    from slots_tracker_server.notifications import Notifications

    charts = requests.get('https://slots-tracker.herokuapp.com/charts/')
    charts_as_json = charts.json()
    for chart in charts_as_json:
        if chart.get('type') == 'table':
            if chart and chart.get('data'):
                message = ''
                for row in chart.get('data'):
                    message += f'{row[0]}: {row[1]}\n'

                Notifications().send('Monthly update', message, target_env)
