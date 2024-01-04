import os
import re
import queue
from ..types.type_def import (
    api_response,
    check_json_keys,
    validate_request_is_json,
)

from multiprocessing.managers import DictProxy, ListProxy
from datetime import datetime
from flask import current_app, request, Blueprint, send_file
from custom_utils import path_utils


DATABASE_TABLE = os.path.splitext(os.path.basename(os.path.realpath(__file__)))[0]
# DATABASE_TABLE = "INSERT CUSTOM NAME FOR PATH"
URL_PREFIX = f"/{DATABASE_TABLE}"

app = current_app
with app.app_context():
    task_queue: queue.Queue = app.config["task_queue"]
    manager_dict: DictProxy = app.config["task_dict"]
    manager_list: ListProxy = app.config["task_list"]
    getLogs = Blueprint(URL_PREFIX, __name__, url_prefix=URL_PREFIX)


@getLogs.route("/get-logs/<string:logType>/<string:date>", methods=["POST", "GET"])
@validate_request_is_json
def get_specific_log(logType, date):
    valid = check_json_keys(["logType", "date"], request.json, return_missing=True)
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


@getLogs.route("/get-all-logs", methods=["GET"])
def get_all_logs():
    output_zip = path_utils.zip_folder("data/logs", "data/logs.zip")
    return send_file(output_zip)
