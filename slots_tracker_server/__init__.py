import os

from flask import Flask
from flask_cors import CORS
from mongoengine import connect

from slots_tracker_server import commands

app = Flask(__name__)
CORS(app)
connect(
    dict(host=os.environ.get('DB_HOST'), port=int(str(os.environ.get('DB_PORT'))),
         username=os.environ.get('DB_USERNAME'), password=os.environ.get('DB_PASS'), name=os.environ.get('DB_NAME')))


import slots_tracker_server.views  # noqa

app.cli.add_command(commands.update_gsheet_header)
