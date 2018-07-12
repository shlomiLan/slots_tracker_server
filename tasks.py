import os

from invoke import task


@task
def run(c):
    os.environ['FLASK_APP'] = 'server'
    os.environ['FLASK_ENV'] = 'development'
    c.run("flask run")


@task
def test(c):
    c.run("pytest")


@task
def test_and_cov(c):
    c.run("pytest -s --cov=slots_tracker --cov-report term-missing")
