__author__ = 'sohje'

import inspect
import datetime
from flask import (Blueprint, Response, render_template, request, g, redirect, jsonify)

# for json-tokens authorization
# import jwt
tasks = Blueprint('tasks', __name__, url_prefix='/tasks')


@tasks.route("/execute/<task_id>", methods=['POST', 'GET'])
def execute_task(task_id):
    from fabric.api import execute
    from StringIO import StringIO
    import sys
    tasks = g.tasks
    task = tasks[task_id]

    output = StringIO()
    error = StringIO()

    sys.stdout = output
    sys.stderr = error
    # todo
    # username
    user_name = 'sohje'
    sdate = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    execute(task)
    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__
    roles = task.wrapped.__dict__['roles']
    deployment = {
        'id': g.db.nipsy.sequence.find_and_modify(
            {"_id": "deploy"},
            {'$inc': {"seq": 1}},
            upsert=True
        )['seq'],
        'fdate': datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        'sdate': sdate,
        'user': user_name,
        # TODO
        # generate status
        'status': 'success',
        'task': task_id,
        'data': output.getvalue(),
        'errors': error.getvalue() or None,
        'roles': g.env.roledefs[roles[0]]
    }
    g.db.nipsy['deployments'].save(deployment)
    return render_template('task/deployed_task.html', deployment=deployment, full=True)

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