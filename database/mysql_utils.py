import pandas as pd
import numpy as np
import datetime


def convert_to_mysql_db_types(column_name: str, data_type: type) -> str:
    mysql_data_type = ""

    if data_type == "int" or data_type == int:
        mysql_data_type = "BIGINT"
    elif data_type == "float" or data_type == float:
        mysql_data_type = "FLOAT"
    elif data_type == "str" or data_type == str:
        mysql_data_type = "VARCHAR(255)"
    elif data_type == "bool" or data_type == bool:
        mysql_data_type = "BOOLEAN"
    elif (
        data_type == "DATETIME"
        or data_type == datetime.date
        or data_type == datetime.time
    ):
        mysql_data_type = "DATETIME"
    # Add more data type mappings as needed

    if mysql_data_type:
        return f"{column_name} {mysql_data_type}"

    raise Exception(f"Failed to convert {column_name} to mysql type {data_type}")


def convert_to_SQL_valid_type(value):
    if isinstance(value, np.generic):
        return type(value.item())
    if isinstance(value, pd._libs.tslibs.timestamps.Timestamp):
        return type(value.date())
    return type(value)
