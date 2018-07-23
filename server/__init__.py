import os

from flask import Flask
from flask_cors import CORS
from flask_mongoengine import MongoEngine


app = Flask(__name__)
CORS(app)

if os.environ.get('FLASK_TEST') == 'true':
    app.config['MONGODB_SETTINGS'] = dict(db='slots_tracker_test')
else:
    app.config['MONGODB_SETTINGS'] = dict(db='slots_tracker')

db = MongoEngine(app)

import server.views  # noqa
