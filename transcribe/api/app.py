import sentry_sdk

import transcribe.db as db
from flask import Flask, g
from transcribe.api import api_bp
from transcribe.db.db_utils import get_flask_db
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn="https://e0115122be6c488a8de28d614b5708d4@o536026.ingest.sentry.io/4504604743499776",
    integrations=[
        FlaskIntegration(),
    ],
    traces_sample_rate=1.0
)

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
    app.run(debug=False, port=6550)
