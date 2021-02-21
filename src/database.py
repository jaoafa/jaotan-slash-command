import json

import mysql.connector as mysqldb


def get_connection():
    with open("config.json") as f:
        config = json.load(f)
        hostname = config["hostname"]
        port = config["port"]
        username = config["username"]
        password = config["password"]
        database = config["database"]

        return mysqldb.connect(
            host=hostname,
            port=port,
            user=username,
            password=password,
            database=database
        )
