from invoke import task
import os


@task
def run(c):
    os.environ['FLASK_APP'] = 'server'
    os.environ['FLASK_ENV'] = 'development'

    c.run("flask run")
