import logging
import os
import sys
from custom_utils import path_utils

from flask_server.types.type_def import check_json

from config.settings import logger, config

import re
import json
import jwt
from datetime import datetime
import threading
import queue
from multiprocessing.managers import DictProxy, ListProxy


from flask import Flask, request, send_file
from flask_socketio import SocketIO, emit
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_server.types.type_def import RaiseAPIException, api_response


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
def status_online():
    if request.method == "POST" or request.method == "GET":
        valid = check_json(["example", "json"], request.json, return_missing=True)
        if valid == True:
            return api_response(
                status=200,
                message="Optional message here",
                data={"key": "value"},
            )
        else:
            raise RaiseAPIException(
                "Missing Field", f"You are missing {valid} field", status_code=400
            )

    raise RaiseAPIException(
        "Invalid Method", "The Method you are calling does not exist", status_code=404
    )


@mainApp.route("/get-logs/<string:logType>/<string:date>", methods=["POST", "GET"])
def get_specific_log(logType, date):
    valid = check_json(["logType", "date"], request.json, return_missing=True)
    if valid == True:
        log_type = request.json["logType"]
        date = request.json["date"]
    else:
        log_type = logType
        log_date = date

    if log_type not in ["debug", "info", "warning", "error"]:
        return api_response(
            status=400,
            message="Valid log types are, [ 'debug' , 'info' , 'warning' , 'error' ]",
            data=request.json,
        )
    elif re.match(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", log_date) is None:
        return api_response(
            status=400,
            message="Date needs to be in 'YYYY-MM-DD' format",
            data=request.json,
        )
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    if log_date == date_str:
        log_to_take = os.path.abspath(os.path.join("data/logs", f"{log_type}.log"))
    else:
        log_to_take = os.path.abspath(
            os.path.join("data/logs", f"{log_type}.log.{log_date}")
        )

    if os.path.exists(log_to_take):
        return send_file(log_to_take)
    else:
        return api_response(
            status=400,
            message="Log does not exist",
            data=request.json,
        )


@mainApp.route("/get-all-logs", methods=["GET"])
def get_all_logs():
    output_zip = path_utils.zip_folder("data/logs", "data/logs.zip")
    return send_file(output_zip)


### ==================== SOCKETIO ========================================


class FlaskServer(threading.Thread):
    def __init__(
        self,
        flask_host: str,
        flask_port: int,
        db_path: str,
        task_queue: queue.Queue,
        task_dict: DictProxy,
        task_list: ListProxy,
        debugging: bool = False,
    ) -> None:
        threading.Thread.__init__(self)
        self.host = flask_host
        self.port = flask_port
        self.debugging = debugging
        self.task_queue = task_queue
        self.task_dict = task_dict
        self.task_list = task_list
        self.database = {
            "object": None,
            "schema": {
                "sampleSchema": {
                    "sampleString": str,
                    "sampleTime": datetime.time,
                    "sampleBool": bool,
                    "sampleInt": int,
                    "sampleFloat": float,
                },
                "sampleTable1": {
                    "sampleString": str,
                    "sampleTime": datetime.time,
                    "sampleBool": bool,
                    "sampleInt": int,
                    "sampleFloat": float,
                },
                "sampleTable2": {
                    "sampleString": str,
                    "sampleTime": datetime.time,
                    "sampleBool": bool,
                    "sampleInt": int,
                    "sampleFloat": float,
                },
            },
        }
        self.run()

    def stop(self):
        self.terminate()

    def run(self):
        mainApp.config["database"] = self.database
        mainApp.config["task_queue"] = self.task_queue
        mainApp.config["task_dict"] = self.task_dict
        mainApp.config["task_list"] = self.task_list
        mainApp.config["settings"] = {"status": True, "message": None}
        with mainApp.app_context():
            from flask_server.routes.sampleTable1 import sampleTable1
            from flask_server.routes.sampleTable2 import sampleTable2

            mainApp.register_blueprint(sampleTable1)
            mainApp.register_blueprint(sampleTable2)

        print(
            f"Starting FLASK server on local network [HostIP: {self.host}:{self.port}]"
        )
        if config["HTTPS"] == True:
            ssl_cert_path = "ssl-cert"
            certfile = os.path.join(ssl_cert_path, "cert.pem")
            keyfile = os.path.join(ssl_cert_path, "key_unencrypted.pem")
            socketio.run(  # HTTPS
                mainApp,
                host=self.host,
                port=self.port,
                ssl_context=(certfile, keyfile),
                allow_unsafe_werkzeug=True,
            )  # Socket + Flask
        else:
            socketio.run(  # HTTP
                mainApp,
                host=self.host,
                port=self.port,
                allow_unsafe_werkzeug=True,
            )
