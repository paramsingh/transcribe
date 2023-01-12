import transcribe.db as db

from flask import Flask, g
from transcribe.api import api_bp
from transcribe.api.db_utils import get_flask_db


app = Flask(__name__)
app.register_blueprint(api_bp, url_prefix="/api/v1")
with app.app_context():
    get_flask_db()


@app.teardown_appcontext
def close_db(e):
    if hasattr(g, "_database"):
        conn = g._database
        if conn is not None:
            conn.close()


if __name__ == "__main__":
    db.create_tables()
    app.run(debug=False, port=6543)
