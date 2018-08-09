import datetime
import json
import os

from invoke import task

from config import BASEDIR

active_venv = 'source {}/venv/bin/activate'.format(BASEDIR)
heroku_app_name = 'slots-tracker'


def run(c, command, with_venv=True):
    if with_venv:
        c.run('{} && {}'.format(active_venv, command))
    else:
        c.run('{}'.format(command))


@task()
def init_app(c, in_heroku=False):
    set_env_var(c, 'APP_SETTINGS', 'config.DevelopmentConfig', in_heroku)
    set_env_var(c, 'FLASK_APP', 'slots_tracker_server', in_heroku)
    set_env_var(c, 'FLASK_ENV', 'development', in_heroku)
    credentials_path = '{}/resources/credentials.json'.format(BASEDIR)
    with open(credentials_path, "r") as read_file:
        set_env_var(c, 'GSHEET_CREDENTIALS', json.load(read_file), in_heroku)


@task(init_app)
def run_app(c):
    run(c, 'flask run')


@task(init_app)
def test(c):
    set_env_var(c, 'APP_SETTINGS', 'config.TestingConfig')
    run(c, 'pytest -s')


@task(init_app)
def test_and_cov(c):
    set_env_var(c, 'APP_SETTINGS', 'config.TestingConfig')
    run(c, 'pytest -s --cov=server --cov-report term-missing')


@task(init_app)
def clean_db(c):
    clean_expenses(c)
    clean_pay_methods(c)


@task(init_app)
def clean_expenses(_):
    # Leave here tp prevent circular import
    from slots_tracker_server.expense import Expense

    print('Removing all expense objects')
    Expense.objects.delete()


@task(init_app)
def clean_pay_methods(_):
    # Leave here tp prevent circular import
    from slots_tracker_server.expense import PayMethods

    print('Removing all pay methods objects')
    PayMethods.objects.delete()


@task(init_app)
def init_db(_):
    insert_base_payments(_)
    insert_base_expense(_)


@task(init_app)
def insert_base_payments(_):
    # Leave here tp prevent circular import
    from slots_tracker_server.expense import PayMethods

    print('Create paying methods')
    PayMethods(name='MasterCard').save()
    PayMethods(name='Visa').save()


@task(init_app)
def insert_base_expense(_):
    # Leave here tp prevent circular import
    from slots_tracker_server.expense import Expense
    from slots_tracker_server.expense import PayMethods

    print('Create expenses')
    Expense(amount=100, description="BBB", pay_method=PayMethods.objects.first(),
            timestamp=datetime.datetime.utcnow).save()


# Heroku
@task(init_app)
def heroku_run(c):
    run(c, 'heroku local', False)


# run scripts
@task(init_app)
def run_command(c, command):
    run(c, 'cd {} && flask {}'.format(BASEDIR, command))


# helper
def set_env_var(c, name, value, in_heroku=False):
    if isinstance(value, dict):
        value = json.dumps(value)
    if in_heroku:
        run(c, "heroku config:set {}='{}' -a {}".format(name, value, heroku_app_name), False)
    else:
        os.environ[name] = value
