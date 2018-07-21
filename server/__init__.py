import os

from flask import Flask
from flask_cors import CORS
from mongoengine import *


app = Flask(__name__)
CORS(app)

print(os.environ.get('FLASK_TEST'))
if (os.environ.get('FLASK_TEST') == 'true'):
    app.config['MONGODB_SETTINGS'] = dict(db='slots_tracker_test')
else:
    app.config['MONGODB_SETTINGS'] = dict(db='slots_tracker')

connect(app.config['MONGODB_SETTINGS'].get('db'))

import server.views  # noqa
