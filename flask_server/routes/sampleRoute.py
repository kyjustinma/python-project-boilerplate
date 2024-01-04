import os
import queue
from multiprocessing.managers import DictProxy, ListProxy

from flask import current_app, request, Blueprint
from ..types.type_def import (
    RaiseAPIException,
    api_response,
    check_json_keys,
    validate_request_is_json,
)

DATABASE_TABLE = os.path.splitext(os.path.basename(os.path.realpath(__file__)))[0]
# DATABASE_TABLE = "INSERT CUSTOM NAME FOR PATH"
URL_PREFIX = f"/{DATABASE_TABLE}"

app = current_app
with app.app_context():
    task_queue: queue.Queue = app.config["task_queue"]
    manager_dict: DictProxy = app.config["task_dict"]
    manager_list: ListProxy = app.config["task_list"]
    sampleRoute = Blueprint(URL_PREFIX, __name__, url_prefix=URL_PREFIX)


@sampleRoute.route("/create", methods=["POST"])
@validate_request_is_json
def create_item():
    check_json_keys(["sampleField"], request.json, return_missing=True)
    return api_response(
        status=200,
        message="Created data",
        data=request.json,
    )


@sampleRoute.route("/read/<uuid>", methods=["GET"])
def read_item(uuid):
    if uuid is None:
        raise RaiseAPIException(
            "Missing Field", f"You are missing uuid in the URL field", status_code=400
        )
    return api_response(
        status=200,
        message=f"{uuid} was requested",
        data={"uuid": uuid},
    )
