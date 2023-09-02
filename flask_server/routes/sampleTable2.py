import os
import sys

import multiprocessing
import queue
from multiprocessing.managers import DictProxy, ListProxy

import json
import re
from datetime import datetime, timezone

from flask import current_app, request, Blueprint, send_file
from ..types.type_def import RaiseAPIException, api_response, check_json
from custom_utils import path_utils


DATABASE_TABLE = "sampleTable2"
URL_PREFIX = f"/{DATABASE_TABLE}"

app = current_app
with app.app_context():
    database = app.config["database"]
    task_queue: queue.Queue = app.config["task_queue"]
    manager_dict: DictProxy = app.config["task_dict"]
    manager_list: ListProxy = app.config["task_list"]
    sampleTable2 = Blueprint(URL_PREFIX, __name__, url_prefix=URL_PREFIX)


@sampleTable2.route("/<string:uuid>", methods=["POST", "GET", "PUT", "DELETE"])
def item_CRUD(uuid):
    if request.method == "POST" or request.method == "PUT":
        valid = check_json(
            database["schema"][DATABASE_TABLE], request.json, return_missing=True
        )
    else:
        valid = check_json(
            database["schema"][DATABASE_TABLE], request.json, return_missing=True
        )

    if valid == True:
        ### TODO: ADD TO Database
        return api_response(
            status=200,
            message=f"{uuid}: Added to database",
            data=request.json,
        )
    elif valid == False:
        raise RaiseAPIException(
            "Incorrect Format",
            "Data is not in json or array of json format",
            status_code=400,
        )
    else:
        raise RaiseAPIException(
            "Missing Field", f"You are missing {valid} field", status_code=400
        )
