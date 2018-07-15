import os

from invoke import task


@task
def run(c):
    os.environ['FLASK_APP'] = 'server'
    os.environ['FLASK_ENV'] = 'development'
    os.environ['FLASK_TEST'] = 'false'
    c.run("flask run")


@task
def test(c):
    os.environ['FLASK_TEST'] = 'true'
    c.run("pytest -s")


@task
def test_and_cov(c):
    c.run("pytest -s --cov=server --cov-report term-missing")


@task
def clean_db(c):
    clean_expense_db(c)


@task
def clean_expense_db(c):
    # Leave here tp prevent circular import
    from server.expense import Expense

    print('Removing all expense objects')
    Expense.objects.delete()
