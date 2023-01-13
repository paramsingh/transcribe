import transcribe.db as db
import schedule
import time
from flask import Flask, g
from transcribe.api import api_bp
from transcribe.db.db_utils import get_flask_db
from transcribe.processor.transcribe import WhisperProcessor


app = Flask(__name__)
app.register_blueprint(api_bp, url_prefix="/api/v1")
app.config['REPLICATE_API_TOKEN'] = "c2b638b386c23db5caf2faedf8ea6e30f968de10"

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

    processor = WhisperProcessor()
    schedule.every(1).minutes.do(processor.process())
    app.run(debug=False, port=6550)
    while True:
        schedule.run_pending()
        time.sleep(1)
