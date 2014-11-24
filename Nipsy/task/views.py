import inspect
import datetime
import gevent

from . import tasks
from .. import socketio, db, fab_tasks, env
from flask import (render_template, g, jsonify, url_for, current_app)
# for json-tokens authorization
# import jwt

def background_execution(app, task_id):
    with app.app_context():
        deploy_id = db.nipsy.sequence.find_and_modify(
            {"_id": "deploy"},
            {'$inc': {"seq": 1}},
            upsert=True
        )['seq']
        user_name = 'sohje'
        from fabric.api import execute
        from StringIO import StringIO
        import sys
        output = StringIO()
        error = StringIO()

        sys.stdout = output
        sys.stderr = error
        tasks = fab_tasks
        task = tasks[task_id]
        # todo
        # username
        sdate = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        roles = task.wrapped.__dict__['roles']
        pre_data = {
            'task': task_id,
            'user': user_name,
            'status': 'info',
            'id': deploy_id,
            'sdate': sdate,
            'fdate': ' ',
            'roles': env.roledefs[roles[0]]
        }
        # python 2.6 bug?
        socketio.emit(
            'my response',
            pre_data,
            namespace='/test'
        )
        db.nipsy['deployments'].save(pre_data)
        execute(task)
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        deployment = {
            'id': int(deploy_id),
            'fdate': datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            'sdate': sdate,
            'user': user_name,
            # TODO
            # generate status
            'status': 'success',
            'task': task_id,
            'data': output.getvalue(),
            'errors': error.getvalue() or None,
            'roles': env.roledefs[roles[0]]
        }
        db.nipsy['deployments'].update({'id': int(deploy_id)}, deployment)
        socketio.emit(
            'my response',
            {
                'task': task_id,
                'user': user_name,
                'status': 'success',
                'id': deploy_id,
                'sdate': sdate,
                'fdate': deployment['fdate'],
                'roles': env.roledefs[roles[0]]
            },
            namespace='/test'
        )

@tasks.route("/execute/<task_id>", methods=['POST'])
def execute_task(task_id):
    app = current_app._get_current_object()
    gevent.spawn(background_execution, app, task_id)
    return jsonify(
        {'deployment': url_for('main.base')}
    )

@tasks.route('/<task_id>')
def view_task(task_id):
    tasks = g.tasks
    try:
        task = tasks[task_id]
        task = task.wrapped
    except KeyError:
        return render_template('404.html'), 404

    roles, hosts = [], []

    while 'wrapped' in task.__dict__:
        if 'roles' in task.__dict__:
            roles = task.__dict__['roles']
        task = task.wrapped

    dict_task = {
        'name': task_id,
        'description': task.__doc__,
        'source': inspect.getsource(task),
        'roles': g.env.roledefs[roles[0]] if roles else None,
    }
    return render_template('task/task.html', task=dict_task)

@tasks.route('/')
def view():
    return render_template('task/view.html', tasks=g.tasks, task_len=len(g.tasks))

@tasks.route('/deployments/<int:task_id>')
def deployed_task(task_id):
    # from DATABASE
    deployment = g.db.nipsy['deployments'].find_one({'id': task_id})
    return render_template('task/deployed_task.html', deployment=deployment, full=True)

@tasks.route('/deployments/')
def deployed_history():
    # from DATABASE
    deployment = g.db.nipsy['deployments'].find().limit(40).sort('sdate', -1)
    return render_template('task/history.html', deployments=deployment)