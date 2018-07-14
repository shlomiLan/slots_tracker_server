
from flask import Flask
from flask_cors import CORS
from flask_mongoengine import MongoEngine


app = Flask(__name__)
CORS(app)

app.config['MONGODB_SETTINGS'] = {
    'db': 'slots_tracker',
}
db = MongoEngine(app)

import server.views  # noqa
