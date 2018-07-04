
from flask import Flask
from mongoengine import *

app = Flask(__name__)
connect('slots_tracker')

import server.views  # noqa
