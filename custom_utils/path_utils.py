import os
import glob
import json


def get_folder_files(path, extension="*.txt", reverse=True):
    path = path + "/" + extension
    list_of_files = glob.glob(path)  # * means all if need specific format then *.csv
    list_of_files.sort(key=os.path.getmtime, reverse=reverse)
    return list_of_files


def check_create_folder(path):
    if os.path.exists(path):
        return path
    else:
        os.makedirs(path)  # Creates all sub directories as needed
        return path


def check_create_file(path):
    if os.path.exists(path):
        return path
    else:
        folder = os.path.dirname(path)
        check_create_file(folder)  # make sure folder for file exists
        with open(path, "w") as _:  # create empty new file
            pass


def json_to_dict(path):
    with open(path) as json_file:
        json_data = json.load(json_file)
    return json_data
