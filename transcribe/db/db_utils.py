import transcribe.db as db
from flask import g
import sqlite3


def get_flask_db() -> sqlite3.Connection:
    connection = getattr(g, "_database", None)
    if connection is None:
        connection = g._database = db.init_db()
    return connection
