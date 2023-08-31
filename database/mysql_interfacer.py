import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))
from config.settings import logger

import datetime
import mysql.connector
import pandas as pd
import numpy as np
import mysql_utils

from databaseTypes import dbSettingsType
from defineSQLSchema import samplePythonSQL_Schema


class mySQLInterfacer:
    def __init__(
        self,
        port: int,
        name: str,
        username: str,
        password: str,
        path: str = "localhost",
    ):
        self.db_info: dbSettingsType = {
            "path": path,
            "port": port,
            "db_name": name,
            "username": username,
            "password": password,
        }
        self._sql_con = None
        self.connect_to_db()
        self.db_schema = samplePythonSQL_Schema

    def connect_to_db(self) -> None:
        self._sql_con = mysql.connector.connect(
            host=self.db_info["path"],
            port=self.db_info["port"],
            user=self.db_info["username"],
            password=self.db_info["password"],
            database=self.db_info["db_name"],
        )

    ### Executes mySQL commands
    def execute_command(self, command: str) -> bool:
        sql_cur = self._sql_con.cursor()
        try:
            logger.debug(f"[mySQL [Command]]: {command}")
            sql_cur.execute(command)
            sql_cur.close()
            self._sql_con.commit()
        except Exception as e:
            logger.error(f"[mySQL [ Error ]]: {e}")
            return False
        return True

    def initialize_tables(
        self, schema_dict: dict[dict[str:type]]
    ) -> list[tuple[bool, str]]:
        """initialize_tables
            Initializes a tables based on a dictionary

        Args:
            schema_dict ( dict[dict[str:type]] ): {"tableName" : {"Columns" : float (Python Type)}}

        Returns:
            list[tuple[bool, str]]: ( Success? , Command sent)
        """
        commands = []
        for tables in schema_dict:
            sql_string = "uuid VARCHAR(255) DEFAULT (uuid()), "  # Alternative "id INT AUTO_INCREMENT PRIMARY KEY,"
            for keys in schema_dict[tables]:
                sql_string += (
                    mysql_utils.convert_to_mysql_db_types(
                        keys, schema_dict[tables][keys]
                    )
                    + ","
                )
            tableName = tables
            sql_string += "createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,"  # createdAt
            sql_string += "lastModifiedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"  # lastModified time
            sql_string = sql_string.rstrip(",")
            commands.append(f"CREATE TABLE if not exists {tableName} ( {sql_string} )")

        command_results = [
            (self.execute_command(command), command) for command in commands
        ]
        return command_results

    def excel_to_dict(self, path: str) -> dict[str : pd.core.frame.DataFrame]:
        """
        Args:
            path (str): Path to Excel Document

        Returns:
            dict[str : pd.core.frame.DataFrame]: { "sheetName" : Panda data frame of sheet}
        """
        xl = pd.ExcelFile(path)
        excel_sheets = {}
        for sheet_name in xl.sheet_names:
            sheet_name = sheet_name.strip()
            df = xl.parse(sheet_name)
            df = df.rename(columns=lambda x: x.strip())
            new_df = df.where(pd.notnull(df), None)
            new_df = new_df.replace({np.nan: None})
            excel_sheets[sheet_name] = new_df
        return excel_sheets

    def convert_excel_dict_to_schema(
        self, excel_dict: dict[str : pd.core.frame.DataFrame]
    ) -> dict[dict[str:type]]:
        """convert_excel_dict_to_schema Converts the excel dictionary to a Schema for mySQL
        Args:
            dict[str : pd.core.frame.DataFrame]: { "sheetName" : Panda data frame of sheet}
        Returns:
            excel_mySQL_schema ( dict[dict[str:type]] ): {"tableName" : {"Columns" : float (Python Type)}}
        """
        excel_mySQL_schema = {}
        for keys in excel_dict.keys():
            if keys == "databaseInformation":
                continue
            excel_mySQL_schema[keys] = {}
            db_column_names = excel_dict[keys].columns
            for column_names in db_column_names:
                column_names = column_names.strip()
                row = 0
                column_type = mysql_utils.convert_to_SQL_valid_type(
                    excel_dict[keys][column_names][row]
                )
                excel_mySQL_schema[keys][column_names] = column_type
        return excel_mySQL_schema

    def insert_custom_table(self, table: str, data: dict) -> tuple[bool, str]:
        """insert_custom_table
            Formats data to "INSERT INTO customers (name, address) VALUES (%s, %s)"
        Args:
            table (str): name of table
            data (dict): data in dict format

        Returns:
            tuple[bool, str]: results of data inserted
        """
        fields = data.keys()
        fields_string = ",".join(fields)
        db_data = ""
        for key in data:
            if key in fields:
                if isinstance(data[key], str):
                    db_data += f"'{data[key]}'" + ","
                elif isinstance(data[key], datetime.date):
                    data_datetime_value = data[key].strftime("%Y-%m-%d %H:%M:%S")
                    db_data += f"'{data_datetime_value}'"
                elif data[key] is None:
                    db_data += str("NULL") + ","
                else:
                    db_data += str(data[key]) + ","
        db_data = db_data.rstrip(",")
        command = f"INSERT INTO {table} ({fields_string}) VALUES ({db_data})"
        return self.execute_command(command), command

    def import_excel_data(
        self, excel_data: dict[str : pd.core.frame.DataFrame]
    ) -> list[tuple[bool, str]]:
        """
        Args:
            dict[str : pd.core.frame.DataFrame]: { "sheetName" : Panda data frame of sheet}

        Returns:
            list[tuple[bool, str]]: results in a list of tuples (Success? , Command)
        """
        commands = []
        for sheets in excel_data:
            sheets = sheets.strip()
            if sheets != "databaseInformation":
                for idx, row in excel_data[sheets].iterrows():
                    result = self.insert_custom_table(
                        sheets, {key: row[key] for key in row.keys()}
                    )
                    commands.append(result)
        return all(commands), commands


if __name__ == "__main__":
    sql_service = mySQLInterfacer(
        path="localhost",
        port=3310,
        name="database_name",
        username="user",
        password="password",
    )
    sql_service.initialize_tables(sql_service.db_schema)
    excel_dict = sql_service.excel_to_dict(path=r"database\excel_mysql_schema.xlsx")
    excel_schema = sql_service.convert_excel_dict_to_schema(excel_dict)
    sql_service.initialize_tables(excel_schema)
    sql_service.insert_custom_table(
        "sampleSchema",
        {
            "sampleString": "testString",
            "sampleTime": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "sampleBool": True,
            "sampleInt": 1234567891,
            "sampleFloat": 1234.5,
        },
    )
    sql_service.insert_custom_table(
        "sampleTable1",
        {
            "sampleBINT": 1234567891,
            "sampleFloat": 1234.5,
            "sampleString": "testString",
            "sampleBool": True,
            "sampleDateTime": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        },
    )
    import_result = sql_service.import_excel_data(excel_dict)
