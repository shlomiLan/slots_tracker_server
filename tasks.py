import datetime
import json
import os

from invoke import task

from config import BASEDIR

active_venv = 'source {}/venv/bin/activate'.format(BASEDIR)
heroku_app_name = 'slots-tracker'


def run(c, command, with_venv=True):
    if with_venv:
        command = '{} && {}'.format(active_venv, command)

    print('Running: {}'.format(command))
    c.run(command)


@task()
def init_app(c, env=None):
    set_env_var(c, 'APP_SETTINGS', 'config.DevelopmentConfig', env)
    set_env_var(c, 'FLASK_APP', 'slots_tracker_server', env)
    set_env_var(c, 'FLASK_ENV', 'development', env)
    credentials_path = '{}/resources/credentials.json'.format(BASEDIR)
    with open(credentials_path, "r") as read_file:
        set_env_var(c, 'GSHEET_CREDENTIALS', json.load(read_file), env)


@task(init_app)
def run_app(c):
    run(c, 'flask run')


@task(init_app)
def test(c, cov=False, file=None):
    # cov - if to use coverage, file - if to run specific file
    set_env_var(c, 'APP_SETTINGS', 'config.TestingConfig', '')
    command = 'pytest -s'
    if cov:
        command = '{} --cov=slots_tracker_server --cov-report term-missing'.format(command)
    if file:
        command = '{} {}'.format(command, file)

    run(c, command)


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
def set_env_var(c, name, value, env):
    # env codes: h - Heroku, t - Travis-CI
    if isinstance(value, dict):
        value = json.dumps(value)
    if env == 'h':
        run(c, "heroku config:set {}='{}' -a {}".format(name, value, heroku_app_name), False)
    elif env == 't':
        run(c, "travis env set {} '{}'".format(name, value), False)
    else:
        os.environ[name] = value
