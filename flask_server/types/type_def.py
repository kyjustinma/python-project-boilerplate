import collections
from typing import Union
from flask import jsonify


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


def check_json(
    keys: list or dict, json: dict or list, return_missing: bool = False
) -> Union[bool, list]:
    """check_json Checks if the keys match the keys in the json

    Args:
        keys (list): keys to check against (schema)
        json (dict or list): the json to be checked
        return_missing (bool, optional): Return the missing keys and index if applicable. Defaults to False.

    Returns:
        Union[bool, list]: Return True/False or missing keys if return_missing set to True
    """
    if isinstance(keys, dict):
        keys = list(keys.keys())
    elif not isinstance(keys, list):  # convert keys to list if its not
        keys = [keys]

    if not (isinstance(json, dict) or isinstance(json, list)):  # Check if list or json
        return False
    if not isinstance(json, list):
        json = [json]  # convert to a list

    missing_keys = {}  # Store missing keys
    for idx, entries in enumerate(json):
        json_keys = entries.keys()
        for k in keys:
            temp = []
            if k not in json_keys:
                if return_missing == True:
                    temp.append(k)
                else:
                    return False  # return false instantly if no return keys
                missing_keys[idx] = temp

    if return_missing == True and bool(missing_keys):
        return missing_keys
    else:
        return True
