import os

from sendgrid import sendgrid, Email
from sendgrid.helpers.mail import Content, Mail


def send_email(subject, content):
    sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY'))
    from_email = Email(name='Slots tracker', email='slots.tracker@gmail.com')
    to_email = Email(name='Slots tracker', email='slots.tracker@gmail.com')
    content = Content("text/plain", content)
    mail = Mail(from_email, subject, to_email, content)
    try:
        sg.client.mail.send.post(request_body=mail.get())
    except Exception as e:
        # TODO: Log error message
        print(e)
