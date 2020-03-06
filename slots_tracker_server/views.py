from datetime import datetime
import json
import os
import subprocess

from slots_tracker_server import app, sentry
from slots_tracker_server.api.expenses import ExpenseAPI, PayMethodsAPI, CategoriesAPI
from slots_tracker_server.charts import Charts
from slots_tracker_server.email import send_email
from slots_tracker_server.notifications import Notifications
from slots_tracker_server.utils import register_api, is_prod

BACKUPS = os.path.join('/tmp', 'backups')


@app.route('/')
def home_page():
    return 'API index page'


@app.route('/charts/')
def charts():
    chart = Charts()
    return chart.clac_charts()


@app.route('/monthly_update/')
def monthly_update():
    res = None
    charts_data = charts()

    if charts_data:
        charts_as_json = json.loads(charts_data)
        for chart in charts_as_json:
            if chart.get('type') == 'table':
                if chart and chart.get('data'):
                    message = ''
                    for row in chart.get('data'):
                        message += f'{row[0]}: {row[1]}\n'

                    res = Notifications().send('Monthly update', message)

        if res is True:
            return 'Message sent'
        else:
            return 'Error occurred, error message: {}'.format(res)

    return f'Empty DB, no monthly update'


def validate_run_response_or_raise(response):
    if response.returncode != 0:
        message = response.stderr.decode('utf-8')
        app.logger.error(message)
        raise Exception(message)


@app.route('/backup/')
def backup():
    today_str = str(datetime.now().date()).replace('-', '_')
    dest_path = os.path.join(BACKUPS, today_str)
    app.logger.info('Backup folder is: {}'.format(dest_path))

    cmd = 'mongodump -h {host}:{port} -d {db_name} -o {dest_path}'.format(
        host=os.environ['DB_HOST'], db_name=os.environ['DB_NAME'], port=os.environ['DB_PORT'], dest_path=dest_path)

    if os.environ.get('DB_USERNAME') and os.environ.get('DB_PASSWORD'):
        cmd += '-u {username} -p {password}'.format(
            username=os.environ['DB_USERNAME'], password=os.environ['DB_PASSWORD'])

    restore_cmd = 'mongorestore -h {host}:{port} {dest_path} --drop'.format(
        host=os.environ['RESTORE_DB_HOST'], db_name=os.environ['DB_NAME'], port=os.environ['DB_PORT'],
        dest_path=dest_path)

    if os.environ.get('RESTORE_DB_USERNAME') and os.environ.get('RESTORE_DB_PASSWORD'):
        cmd += '-u {username} -p {password}'.format(
            username=os.environ['RESTORE_DB_USERNAME'], password=os.environ['RESTORE_DB_PASSWORD'])

    try:
        res = subprocess.run(cmd.split(), capture_output=True)
        validate_run_response_or_raise(res)
        res = subprocess.run(restore_cmd.split(), capture_output=True)
        validate_run_response_or_raise(res)

        msg = f'The {today_str} DB backup in {os.environ["FLASK_ENV"]} was restored successfully.'
    except Exception as e:
        msg = str(e)

    if is_prod():
        send_email(subject='DB restore test', content=msg)

    return msg


if not app.debug:
    @app.errorhandler(Exception)
    def handle_general_exception(e):
        app.logger.error(e)
        sentry.captureException()
        code = 400
        if hasattr(e, 'code'):
            code = e.code

        return "An error occurred, I'm on it to fix it :-)", code


register_api(ExpenseAPI, 'expense_api', '/expenses/', pk='obj_id')
register_api(PayMethodsAPI, 'pay_methods_api', '/pay_methods/', pk='obj_id')
register_api(CategoriesAPI, 'categories_api', '/categories/', pk='obj_id')
