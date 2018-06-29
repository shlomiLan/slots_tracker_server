from invoke import task


@task
def run(c):
    c.run("python server.py")


@task
def test(c):
    c.run("python -m pytest")


@task
def test_and_cov(c):
    c.run("py.test --cov=slots_tracker --cov-report html")
