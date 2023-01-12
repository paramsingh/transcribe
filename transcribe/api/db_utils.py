import transcribe.db as db
from flask import g


def get_flask_db():
    connection = getattr(g, "_database", None)
    if connection is None:
        connection = g._database = db.init_db()
    return connection
