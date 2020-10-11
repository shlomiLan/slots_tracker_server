import os

from flask import Flask
from flask_cors import CORS
from mongoengine import connect
from raven.contrib.flask import Sentry

app = Flask(__name__)
CORS(app)

DB_HOST = os.environ.get('DB_HOST')
DB_NAME = os.environ.get('DB_NAME')
DB_USERNAME = os.environ.get('DB_USERNAME')
DB_PASSWORD = os.environ.get('DB_PASS')
# TODO: fix on localhost / tests
DB_URI_TEMPLATE = os.environ['DB_URI_TEMPLATE']
DB_URI = DB_URI_TEMPLATE.format(DB_HOST=DB_HOST, DB_NAME=DB_NAME, DB_USERNAME=DB_USERNAME, DB_PASSWORD=DB_PASSWORD)
connect(host=DB_URI)

sentry = Sentry(app, dsn=os.environ.get('SENTRY_DSN'))

import slots_tracker_server.views  # noqa
