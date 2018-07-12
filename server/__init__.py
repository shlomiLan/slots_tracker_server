
from flask import Flask
from flask_cors import CORS
from mongoengine import *


app = Flask(__name__)
CORS(app)
connect('slots_tracker')

import server.views  # noqa
