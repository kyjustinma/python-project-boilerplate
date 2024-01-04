import logging
import os
import json
import threading
import queue

from config.settings import logger, ENV_CONFIG
from multiprocessing.managers import DictProxy, ListProxy


from flask import Flask, request
from flask_socketio import SocketIO
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_server.types.type_def import (
    RaiseAPIException,
    api_response,
    check_json_keys,
    validate_request_is_json,
)


### Logging built in the Flask server (does not log to file)
log = logging.getLogger("werkzeug")
log.setLevel(logging.WARN)

# Local Server
mainApp = Flask(__name__)
mainApp.config["JSON_SORT_KEYS"] = False
socketio = SocketIO(mainApp, cors_allowed_origins="*")
limiter = Limiter(
    get_remote_address, app=mainApp, default_limits=["5/second"]
)  # Rate limiter


### ==================== SOCKETIO ========================================
@socketio.on("connect")
def on_connect(auth):
    socketio.emit("logs", "User Connected")
    print("Client connected")


@socketio.on("disconnect")
def on_disconnect():
    socketio.emit("logs", "User Disconnected")
    print("Client disconnected")


@socketio.on("logs")
def handle_message(data):
    socketio.emit("logs", data)
    # if data == "command:kill_server":
    #     threading.Timer(1, socketio.stop()).start()  # set timer for two seconds


### Handle Rate limited requests
@mainApp.errorhandler(429)
def ratelimit_handler(e):
    return "You have exceeded your rate-limit"


### This handles all other exceptions in the server
@mainApp.errorhandler(Exception)
def http_error_handler(e):
    """Return JSON instead of HTML for HTTP errors."""
    # start with the correct headers and status code from the error
    response = e.get_response()
    # replace the body with JSON
    standard_response, _ = api_response(
        status=e.code, message=f"{e.name} : {e.description}"
    )
    response.data = json.dumps(standard_response)
    response.content_type = "application/json"
    logger.error(response)
    socketio.emit("logs", response)
    return response


### this handles specific error such as typing errors
@mainApp.errorhandler(RaiseAPIException)
def handle_invalid_usage(error):
    response = error.get_response()
    try:
        message = f"{response}"
        socketio.emit("logs", message)
        logger.error(message)
    except:
        logger.error(response)

    return response


### Logs to log all the requests made
@mainApp.before_request
def log_request():
    try:
        message = f"{request}: {request.json}"
        socketio.emit("logs", message)
        logger.info(message)
    except:
        message = f"{request}"
        socketio.emit("logs", message)
        logger.info(request)


@mainApp.after_request
def log_response(response):
    try:
        message = f"{response}: {response.json}"
        socketio.emit("logs", message)
        logger.info(message)
    except:
        message = f"{response}"
        socketio.emit("logs", message)
        logger.info(response)
    return response


@mainApp.route("/", methods=["POST", "GET", "PUT", "DELETE"])
@validate_request_is_json
def status_online():
    if request.method == "POST":
        valid = check_json_keys(["example", "json"], request.json, return_missing=True)
    return api_response(
        status=200,
        message="Optional message here",
        data={"key": "value"},
    )


### ==================== SOCKETIO ========================================


class FlaskServer(threading.Thread):
    def __init__(
        self,
        flask_host: str,
        flask_port: int,
        https: bool,
        task_queue: queue.Queue,
        task_dict: DictProxy,
        task_list: ListProxy,
        debugging: bool = False,  # FALSE when in process
    ) -> None:
        threading.Thread.__init__(self)
        self.host = flask_host
        self.port = flask_port
        self.https = https
        self.debugging = debugging
        self.task_queue = task_queue
        self.task_dict = task_dict
        self.task_list = task_list
        self.run()

    def stop(self):
        self.terminate()

    def run(self):
        mainApp.config["task_queue"] = self.task_queue
        mainApp.config["task_dict"] = self.task_dict
        mainApp.config["task_list"] = self.task_list
        mainApp.config["settings"] = {"status": True, "message": None}
        with mainApp.app_context():
            from flask_server.routes.sampleRoute import sampleRoute

            mainApp.register_blueprint(sampleRoute)

        print(
            f"Starting FLASK server on local network [HostIP: {self.host}:{self.port}]"
        )
        if self.https == True:
            ssl_cert_path = "ssl-cert"
            certfile = os.path.join(ssl_cert_path, "cert.pem")
            keyfile = os.path.join(ssl_cert_path, "key_unencrypted.pem")
            socketio.run(  # HTTPS
                mainApp,
                host=self.host,
                port=self.port,
                ssl_context=(certfile, keyfile),
                debug=self.debugging,
                allow_unsafe_werkzeug=True,
            )  # Socket + Flask
        else:
            socketio.run(  # HTTP
                mainApp,
                host=self.host,
                port=self.port,
                debug=self.debugging,
                allow_unsafe_werkzeug=True,
            )
