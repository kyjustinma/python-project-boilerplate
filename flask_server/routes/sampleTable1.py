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


DATABASE_TABLE = "sampleTable1"
URL_PREFIX = f"/{DATABASE_TABLE}"

app = current_app
with app.app_context():
    database = app.config["database"]
    task_queue: queue.Queue = app.config["task_queue"]
    manager_dict: DictProxy = app.config["task_dict"]
    manager_list: ListProxy = app.config["task_list"]
    sampleTable1 = Blueprint(URL_PREFIX, __name__, url_prefix=URL_PREFIX)


@sampleTable1.route("/create", methods=["POST"])
def create_item():
    valid = check_json(
        database["schema"][DATABASE_TABLE], request.json, return_missing=True
    )
    if valid == True:
        ### TODO: ADD TO Database
        return api_response(
            status=200,
            message="Added to database",
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


@sampleTable1.route("/read", methods=["GET"])
def read_item():
    valid = check_json(["uuid"], request.json, return_missing=True)
    if valid == True:
        uuid = request.json["uuid"]
        ### TODO: READ Database
        db_data = {"uuid": uuid}
        return api_response(
            status=200,
            message=f"{uuid} was returned",
            data=db_data,
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


@sampleTable1.route("/update", methods=["PUT"])
def update_item():
    valid = check_json(
        database["schema"][DATABASE_TABLE], request.json, return_missing=True
    )
    if valid == True:
        uuid = request.json["uuid"]
        ### TODO: UPDATE TO Database

        return api_response(
            status=200,
            message=f"{uuid}: Updated",
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


@sampleTable1.route("/remove", methods=["DELETE"])
def remove_item():
    valid = check_json(["uuid"], request.json, return_missing=True)
    if valid == True:
        uuid = request.json["uuid"]
        ### TODO: REMOVE from Database
        return api_response(status=200, message=f"{uuid}: Removed from database")
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
