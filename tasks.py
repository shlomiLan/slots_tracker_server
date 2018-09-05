import json
import os

import yaml
from invoke import task, call

BASEDIR = os.path.abspath(os.path.dirname(__file__))
active_venv = 'source {}/venv/bin/activate'.format(BASEDIR)
heroku_app_name = 'slots-tracker'


def run(c, command, with_venv=True):
    if with_venv:
        command = '{} && {}'.format(active_venv, command)

    print('Running: {}'.format(command))
    c.run(command)


@task()
def init_app(c, env=None, settings=None):
    # Load the basic configs
    env_vars = load_yaml_from_file('{}/resources/settings.yml'.format(BASEDIR))

    if settings:
        env_vars.update(load_yaml_from_file('{}/resources/settings_{}.yml'.format(BASEDIR, settings)))

    for name, data in env_vars.items():
        set_env_var(c, name, data.get('value'), env, data.get('is_protected', False))


@task(init_app)
def run_app(c):
    run(c, 'flask run')


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
def clean_db(c):
    clean_expenses(c)
    clean_pay_methods(c)
    clean_categories(c)


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
    clean_db(c)
    initial_data = load_yaml_from_file('{}/resources/init_db.yml'.format(BASEDIR))
    # Leave here tp prevent circular import
    from slots_tracker_server.models import PayMethods
    from slots_tracker_server.models import Categories
    insert_db_data(PayMethods, initial_data.get('pay_methods'))
    insert_db_data(Categories, initial_data.get('categories'))


def insert_db_data(cls, db_data):
    print('Creating {}'.format(cls.__name__))

    for item in db_data:
        cls(name=item).save()


@task()
def update_requirements(c):
    run(c, 'pip install -r development.txt')


# Heroku
@task(init_app)
def heroku_run(c):
    run(c, 'heroku local', False)


# run scripts
@task(init_app)
def run_command(c, command):
    run(c, 'cd {} && flask {}'.format(BASEDIR, command))


# helper
def set_env_var(c, name, value, env, is_protected=True):
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
        os.environ[name] = value


def load_yaml_from_file(file_path):
    with open(file_path, 'r') as stream:
        return yaml.safe_load(stream)
