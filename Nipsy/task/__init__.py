from flask import Blueprint

tasks = Blueprint('tasks', __name__, url_prefix='/tasks')

from . import views
