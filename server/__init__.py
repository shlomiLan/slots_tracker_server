import os

from flask import Flask
from flask_cors import CORS
from flask_mongoengine import MongoEngine


app = Flask(__name__)
CORS(app)

print(os.environ.get('FLASK_TEST'))
if (os.environ.get('FLASK_TEST') == 'true'):
    app.config['MONGODB_SETTINGS'] = dict(db='slots_tracker1111')
else:
    app.config['MONGODB_SETTINGS'] = dict(db='slots_tracker')

print(app.config['MONGODB_SETTINGS'])

db = MongoEngine(app)

import server.views  # noqa
