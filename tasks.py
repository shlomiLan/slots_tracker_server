from invoke import task


@task
def run(c):
    c.run("python server.py")


@task
def test(c):
    c.run("pytest")


@task
def test_and_cov(c):
    c.run("pytest -s --cov=slots_tracker --cov-report term-missing")
