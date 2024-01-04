import collections
from typing import Union
from flask import jsonify
from functools import wraps
from flask import request


def validate_request_is_json(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not isinstance(request.json, dict):
            raise RaiseAPIException(
                "Request body incorrect format",
                "Validator: Data is not in json format",
                status_code=400,
            )
        return func(*args, **kwargs)

    return wrapper


class RaiseAPIException(Exception):
    status_code = 400

    def __init__(
        self, name: str, message: str, status_code: int = None, payload: dict = None
    ):
        super().__init__()
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

        if payload is not None:
            self.response = {
                "code": self.status_code,
                "name": name,
                "msg": message,
                "data": payload,
            }
        else:
            self.response = {
                "code": self.status_code,
                "name": name,
                "msg": message,
            }

    def get_response(self):
        return jsonify(self.response), self.status_code


def api_response(status: int, msg: str = None, data: dict = None, **kwargs: str):
    response = {"code": status}

    for key, value in kwargs.items():
        response[key] = value

    if msg is not None:
        response["msg"] = msg

    if data is not None:
        response["data"] = data

    return response, status


def check_json_keys(
    keys: dict or list,
    json: dict or list,
    return_missing: bool = False,
    raise_exception: bool = True,
) -> Union[bool, list]:
    """check_json Checks if the keys match the keys in the json

    Args:
        keys (dict or list): keys to check against (schema)
        json (dict or list): The json to be checked
        return_missing (bool, optional): Return the missing keys and index if applicable. Defaults to False.

    Returns:
        Union[bool, list]: Return True/False or missing keys if return_missing set to True
    """
    if not (isinstance(json, list) or isinstance(json, dict)):
        raise RaiseAPIException(
            "Request body incorrect format",
            "Validator: Data is not in json format",
            status_code=400,
        )

    if isinstance(keys, dict):
        keys = list(keys.keys())
    if not isinstance(keys, list):  # convert keys to list if its not
        keys = [keys]
    if not isinstance(json, list):  # Ensure that its a list
        json = [json]

    missing_keys = {}  # Store missing keys
    for idx, entries in enumerate(json):  # case that its a list
        json_keys = entries.keys()
        for k in keys:
            temp = []
            if k not in json_keys:
                if return_missing == True:
                    temp.append(k)
                else:
                    if raise_exception:
                        raise RaiseAPIException(
                            "Missing Field",
                            f"You are missing a field",
                            status_code=400,
                        )
                    return False  # return false instantly if no return keys
                missing_keys[idx] = temp

    if return_missing == True and bool(missing_keys):
        if raise_exception:
            raise RaiseAPIException(
                "Missing Field",
                f"You are missing {missing_keys} field",
                status_code=400,
            )
        return missing_keys

    return True
