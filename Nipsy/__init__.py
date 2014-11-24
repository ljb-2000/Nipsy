__author__ = 'sohje'
__version__ = 0.02

import pymongo
from flask import Flask, g
from flask.ext.socketio import SocketIO
from fabric import main as fab_main
import config
from fabfile import env

def connect(host, port):
    client = False
    try:
        client = pymongo.MongoClient(host, port)
    except pymongo.errors.ConnectionFailure, messages:
        print messages

    if config.MONGO_USER and config.MONGO_PW:
        auth = client['admin']
        try:
            auth.authenticate(config.MONGO_USER, config.MONGO_PW)
        except KeyError:
            raise Exception('KeyError: Not authenticating!')
    return client

socketio = SocketIO()
db = connect(config.MONGO_HOST, config.MONGO_PORT)
docstring, fab_tasks = fab_main.load_fabfile(config.fabfile)[:2]

def create_app(debug=False):
    app = Flask(__name__)

    @app.before_request
    def before_request():
        g.docstring, g.tasks = fab_main.load_fabfile(config.fabfile)[:2]
        g.env, g.env.user, g.env.key_filename = env, config.user, config.key_filename
        g.db = connect(config.MONGO_HOST, config.MONGO_PORT)

    app.debug = debug
    from main import main as main_blueprint
    from task import tasks as task_blueprint
    app.register_blueprint(main_blueprint)
    app.register_blueprint(task_blueprint)
    socketio.init_app(app)
    return app