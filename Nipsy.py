from flask import Flask, render_template, g, jsonify
import pymongo

# blueprints
from task.views import tasks

from fabric import main
from fabfile import env
import config

app = Flask(__name__)
app.config['DEBUG'] = True


def _connect(host, port):
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


@app.before_request
def before_request():
    g.docstring, g.tasks = main.load_fabfile(config.fabfile)[:2]
    g.env, g.env.user, g.env.key_filename = env, config.user, config.key_filename
    g.db = _connect(config.MONGO_HOST, config.MONGO_PORT)


@app.route('/')
def base():
    deployment = g.db.nipsy['deployments'].find().limit(5).sort('sdate', -1)
    return render_template('index.html', deployments=deployment, roles=g.env.roledefs)


@app.route('/settings')
def settigs():
    settings = {
        'fabfile': config.fabfile,
        'mongo host': config.MONGO_HOST,
        'mongo port': config.MONGO_PORT,
        'mongo db': config.MONGO_DB,
        'user': config.user,
        'key': config.key_filename,
        'deployments': g.db.nipsy['deployments'].count(),
        'email notifications': False
    }
    return jsonify(settings)

app.register_blueprint(tasks)


if __name__ == '__main__':
    app.run()
