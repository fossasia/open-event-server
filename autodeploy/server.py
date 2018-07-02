import json
import logging
from flask import Flask
from docker import DockerCompose

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
docker = DockerCompose(cwd='../open-event-server')


@app.route('/ps')
def ps():
    return json.dumps(docker.ps())


@app.route('/start')
def start():
    docker.start()
    return json.dumps(docker.ps())


@app.route('/stop')
def stop():
    docker.stop()
    return json.dumps(docker.ps())


if __name__ == '__main__':
    app.run()
