import datetime
import os

from invoke import task


@task
def active_venv(c):
    c.run('source venv/bin/activate')


@task
def init_app(c):
    os.environ['APP_SETTINGS'] = 'config.DevelopmentConfig'
    os.environ['FLASK_APP'] = 'slots_tracker_server'
    active_venv(c)


@task(init_app)
def run(c):
    os.environ['FLASK_ENV'] = 'development'
    # os.environ['FLASK_TEST'] = 'false'
    c.run("flask run")


@task(init_app)
def test(c):
    # os.environ['FLASK_TEST'] = 'true'
    print(os.environ['APP_SETTINGS'])
    os.environ['APP_SETTINGS'] = 'config.TestingConfig'
    print(os.environ['APP_SETTINGS'])
    c.run("pytest -s")


@task(init_app)
def test_and_cov(c):
    os.environ['APP_SETTINGS'] = 'config.TestingConfig'
    c.run("pytest -s --cov=server --cov-report term-missing")


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
    c.run('heroku local')
