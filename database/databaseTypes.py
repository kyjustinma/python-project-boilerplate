from typing import TypedDict


# Types should be PascalCase
class dbSettingsType(TypedDict):
    path: str
    port: int
    db_name: str
    username: str
    password: str
