from invoke import task

from pyinvoke.base import init_app


@task(init_app)
def email(_, subject='First email', content='Hey, \nthis is a test email from the app:-)'):
    from slots_tracker_server.email import send_email
    send_email(subject=subject, content=content)
