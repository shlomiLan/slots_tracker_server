import datetime
import json
import os

import yaml
from invoke import task, call
from mongoengine import DoesNotExist

BASEDIR = os.path.abspath(os.path.dirname(__file__))

BACKUPS = os.path.join(BASEDIR, 'backups')


def run(c, command, with_venv=True):
    if with_venv:
        command = '{} && {}'.format(get_venv_action(), command)

    print('Running: {}'.format(command))
    c.run(command)


@task()
def init_app(c, env=None, settings=None):
    print(f'settings is: {settings}')
    # Prevent execute this function more than once
    if not os.environ.get('APP_SETTINGS'):
        # Load the basic configs
        env_vars = load_yaml_from_file(os.path.join(BASEDIR, 'resources', 'settings.yml'))

        if settings:
            env_vars.update(load_yaml_from_file(os.path.join(BASEDIR, 'resources', f'settings_{settings}.yml')))

        heroku_app_name = env_vars.pop('HEROKU_APP_NAME').get('value')
        for name, data in env_vars.items():
            set_env_var(c, name, data.get('value'), env, data.get('is_protected', False), heroku_app_name)


@task(init_app)
def run_app(c):
    run(c, 'flask run')


@task()
def clean_db(c, settings=None):
    init_app(c, settings=settings)
    clean_expenses(c)
    clean_pay_methods(c)
    clean_categories(c)


@task(call(init_app, settings='test'))
def test(c, cov=False, file=None):
    # cov - if to use coverage, file - if to run specific file

    command = 'pytest -s'
    if cov:
        command = '{} --cov=slots_tracker_server --cov-report term-missing'.format(command)
    if file:
        command = '{} {}'.format(command, file)

    run(c, command)


@task(init_app)
def clean_expenses(_):
    # Leave here tp prevent circular import
    from slots_tracker_server.models import Expense

    print('Removing all expense objects')
    Expense.objects.delete()


@task(init_app)
def clean_pay_methods(_):
    # Leave here tp prevent circular import
    from slots_tracker_server.models import PayMethods

    print('Removing all pay methods objects')
    PayMethods.objects.delete()


@task(init_app)
def clean_categories(_):
    # Leave here tp prevent circular import
    from slots_tracker_server.models import Categories

    print('Removing all pay methods objects')
    Categories.objects.delete()


@task()
def init_db(c, env=None, settings=None):
    init_app(c, env, settings)
    clean_db(c, settings)
    initial_data = load_yaml_from_file(os.path.join(BASEDIR, 'resources', 'init_db.yml'))
    # Leave here tp prevent circular import
    from slots_tracker_server.models import PayMethods, Categories
    insert_db_data(PayMethods, initial_data.get('pay_methods'))
    insert_db_data(Categories, initial_data.get('categories'))


def insert_db_data(cls, db_data):
    print('Creating {}'.format(cls.__name__))

    for item in db_data:
        cls(name=item).save()


@task()
def update_requirements(c):
    run(c, 'pip install -r development.txt')


# DB
@task()
def backup_db(c, settings='prod', force_restore=False):
    init_app(c, settings=settings)
    host, port, db_name, username, password = get_db_info()
    today_str = str(datetime.datetime.now().date()).replace('-', '_')
    dest_path = os.path.join(BACKUPS, today_str)
    run(c, f'mongodump -h {host}:{port} -d {db_name} -u {username} -p {password} -o {dest_path}', False)

    day = datetime.datetime.now().day
    # If first backup of the month or force
    if day <= 7 or force_restore:
        restore_db(c, today_str)
        email(c, subject='DB restore test', content=f'The {today_str} daily backup was restored to stage successfully.')


@task()
def restore_db(c, date, backup_db_name='slots_tracker', settings='stage'):
    init_app(c, settings=settings)
    host, port, db_name, username, password = get_db_info()
    source_path = os.path.join(BACKUPS, date, backup_db_name)
    run(c, f'mongorestore -h {host}:{port} -d {db_name} -u {username} -p {password} {source_path} --drop', False)


@task()
def sync_db_from_gsheet(c, settings=None, reset_db=True):
    init_app(c, settings=settings)
    if reset_db:
        init_db(c, settings=settings)

    import slots_tracker_server.gsheet as gsheet
    wks = gsheet.get_worksheet()
    headers = gsheet.get_headers(wks)
    last_row = gsheet.find_last_row(wks)
    g_data = gsheet.get_all_data(wks)

    # skip the headers row
    for i, row in enumerate(g_data[1:last_row], start=2):
        expense_data = row[:gsheet.end_column_as_number()]
        # Only write to DB rows without id
        if not expense_data[0]:
            print(f'Processing row number: {i}')
            expense_dict = transform_expense_to_dict(expense_data, headers)
            translate(expense_dict)
            reference_objects_str_to_id(expense_dict)
            clean_expense(expense_dict)

            from slots_tracker_server.models import Expense
            expense = Expense(**expense_dict).save()
            # Update the id column
            gsheet.update_with_retry(wks, row=i, col=1, value=str(expense.id))


# Heroku
@task(init_app)
def heroku_run(c):
    run(c, 'heroku local', False)


# run scripts
@task(init_app)
def run_command(c, command):
    run(c, 'cd {} && flask {}'.format(BASEDIR, command))


# email
@task(init_app)
def email(_, subject='First email', content='Hey, \nthis is a test email from the app:-)'):
    from slots_tracker_server.email import send_email
    send_email(subject=subject, content=content)


# helper
def set_env_var(c, name, value, env, is_protected=True, heroku_app_name=None):
    # env codes: h - Heroku, t - Travis-CI
    if isinstance(value, dict):
        value = json.dumps(value)

    if env in ['h', 't']:
        command = ''
        if env == 'h':
            command = "heroku config:set {}='{}' -a {}".format(name, value, heroku_app_name)
        elif env == 't':
            command = "travis env set {} '{}'".format(name, value)
            if not is_protected:
                command = '{} --public'.format(command)

        if command:
            run(c, command, False)

    else:
        print(f'Set local var: {name}={value}')
        os.environ[name] = value


def get_db_info():
    return os.environ['DB_HOST'], os.environ['DB_PORT'], os.environ['DB_NAME'], os.environ['DB_USERNAME'], \
           os.environ['DB_PASS']


def load_yaml_from_file(file_path):
    with open(file_path, 'r') as stream:
        return yaml.safe_load(stream)


def is_unix():
    return os.name == 'posix'


def get_venv_action():
    if is_unix():
        return f'source {BASEDIR}/venv/bin/activate'
    else:
        return f'{BASEDIR}\\venv\\Scripts\\activate'


def translate(expense_data):
    trans_data = load_yaml_from_file(os.path.join(BASEDIR, 'resources', 'translate.yml'))

    for k, v in expense_data.items():
        if trans_data.get(k):
            if trans_data[k].get(v):
                expense_data[k] = trans_data[k][v]


def transform_expense_to_dict(expense_data, headers):
    return {headers[i].value: expense_data[i] for i in range(len(expense_data))}


def reference_objects_str_to_id(expense_data):
    from slots_tracker_server.models import PayMethods, Categories
    try:
        expense_data['pay_method'] = PayMethods.objects.get(name=expense_data.get('pay_method'))
        expense_data['category'] = Categories.objects.get(name=expense_data.get('category'))
    except DoesNotExist:
        print(f'Error in pay method or category: {expense_data.get("pay_method")} and {expense_data.get("category")}')


def clean_expense(expense_data):
    del expense_data['_id']
    expense_data['amount'] = expense_data.get('amount').replace(',', '')
    expense_data['one_time'] = expense_data['one_time'] == 'one_time'
    if '/' in expense_data['timestamp']:
        day, month, year = expense_data['timestamp'].split('/')
        expense_data['timestamp'] = f'20{year}-{month}-{day}'
