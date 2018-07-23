import os

from flask import Flask
from flask_cors import CORS
from flask_mongoengine import MongoEngine


app = Flask(__name__)
CORS(app)

if os.environ.get('FLASK_TEST') == 'true':
    app.config['MONGODB_SETTINGS'] = dict(db='slots_tracker_test')
else:
    app.config['MONGODB_SETTINGS'] = {
        'db': 'slots_tracker',
        'host': 'mongodb://ds145921.mlab.com/slots_tracker',
        'port': 45921,
        'username': 'slots_tracker',
        'password': 'Q77GdN2^S$0r'
    }

db = MongoEngine(app)

import slots_tracker_server.views  # noqa
