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
    clean_expenses(c)
    clean_pay_methods(c)


@task
def clean_expenses(c):
    # Leave here tp prevent circular import
    from server.expense import Expense

    print('Removing all expense objects')
    Expense.objects.delete()


@task
def clean_pay_methods(c):
    # Leave here tp prevent circular import
    from server.expense import PayMethods

    print('Removing all pay methods objects')
    PayMethods.objects.delete()


@task
def init_db(c):
    insert_base_payments()
    insert_base_expense()


def insert_base_payments():
    # Leave here tp prevent circular import
    from server.expense import PayMethods

    print('Create paying methods')
    PayMethods(name='MasterCard').save()
    PayMethods(name='Visa').save()


def insert_base_expense():
    # Leave here tp prevent circular import
    from server.expense import Expense
    from server.expense import PayMethods

    print('Create expenses')
    Expense(amount=100, descreption="BBB", pay_method=PayMethods.objects.first()).save()
