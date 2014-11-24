#!/bin/env python
from gevent import monkey
monkey.patch_all()

from Nipsy import create_app, socketio
from Nipsy import config
app = create_app(True)

if __name__ == '__main__':
    socketio.run(app, host=config.HOST, port=config.PORT)
