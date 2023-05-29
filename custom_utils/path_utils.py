import os
import glob


def get_folder_files(path, extension="*.txt", reverse=True):
    path = path + "/" + extension
    list_of_files = glob.glob(path)  # * means all if need specific format then *.csv
    list_of_files.sort(key=os.path.getmtime, reverse=reverse)
    return list_of_files
