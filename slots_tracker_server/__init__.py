import os

from flask import Flask
from flask_mongoengine import MongoEngine


app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])

db = MongoEngine(app)

import slots_tracker_server.views  # noqa
