from flask import (render_template, g, jsonify)
from flask.ext.socketio import emit

from . import main
from .. import socketio
from .. import config


@main.route('/')
def base():
    deployment = g.db.nipsy['deployments'].find().limit(5).sort('sdate', -1)
    return render_template('index.html', deployments=deployment, roles=g.env.roledefs)


@main.route('/settings')
def settings():
    conf_settings = {
        'fabfile': config.fabfile,
        'mongo host': config.MONGO_HOST,
        'mongo port': config.MONGO_PORT,
        'mongo db': config.MONGO_DB,
        'user': config.user,
        'key': config.key_filename,
        'deployments': g.db.nipsy['deployments'].count(),
        'email notifications': False
    }
    return jsonify(conf_settings)


@socketio.on('my event', namespace='/test')
def test_message(message):
    emit('my response', {'data': message['data'], 'status': message['status']}, broadcast=True)
