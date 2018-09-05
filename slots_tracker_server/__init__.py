import os

from flask import Flask
from flask_cors import CORS
from mongoengine import connect

from slots_tracker_server import commands

app = Flask(__name__)
CORS(app)
app.config.from_object(os.environ['APP_SETTINGS'])
connect(**app.config.get('MONGODB_SETTINGS'))


import slots_tracker_server.views  # noqa

app.cli.add_command(commands.update_gsheet_header)
