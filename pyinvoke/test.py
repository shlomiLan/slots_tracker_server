import os

from invoke import task, call

from pyinvoke.base import init_app
from pyinvoke.utils import run


@task(call(init_app, settings='test'))
def test(c, cov=False, file=None):
    # cov - if to use coverage, file - if to run specific file
    os.environ['TESTING'] = 'true'
    os.environ['DB_NAME'] = 'slots_tracker_test'

    command = 'pytest -s --disable-pytest-warnings'
    if cov:
        command = '{} --cov=slots_tracker_server --cov-report term-missing'.format(command)
    if file:
        command = '{} {}'.format(command, file)

    run(c, command)
