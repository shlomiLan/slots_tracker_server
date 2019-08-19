import os

from flask import Flask
from flask_cors import CORS
from mongoengine import connect
from raven.contrib.flask import Sentry

from slots_tracker_server import commands

app = Flask(__name__)
CORS(app)
connect(host=os.environ.get('DB_HOST'), port=int(str(os.environ.get('DB_PORT'))),
        username=os.environ.get('DB_USERNAME'), password=os.environ.get('DB_PASS'), name=os.environ.get('DB_NAME'),
        retryWrites=False)
sentry = Sentry(app, dsn=os.environ.get('SENTRY_DSN'))

import slots_tracker_server.views  # noqa
