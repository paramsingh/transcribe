import typing
import os

from flask_cors import cross_origin  # type: ignore
from flask import Blueprint, jsonify, Response, request, send_file
from transcribe.db.db_utils import get_flask_db
import transcribe.db.transcription as transcription_db
from transcribe.processor.transcribe import get_downloaded_file_path

api_bp = Blueprint("api_v1", __name__)


@api_bp.route("/transcribe", methods=["POST"])
@cross_origin()
def transcribe() -> Response:
    request_data = typing.cast(typing.Dict[str, str], request.get_json())
    link = request_data.get("link")
    if not link:
        return jsonify({"error": "no link"}), 400
    db = get_flask_db()
    uuid = transcription_db.create_transcription(db, link, None)
    return jsonify({"id": uuid})


@api_bp.route("/transcription/<uuid>/details", methods=["GET"])
@cross_origin()
def get_transcription(uuid) -> Response:
    if not uuid:
        return jsonify({"error": "no uuid"}), 400
    db = get_flask_db()
    result = transcription_db.get_transcription(db, uuid)
    if not result:
        return jsonify({"error": "not found"}), 404
    return jsonify(result)


@api_bp.route("/internal/transcription/<uuid>/file", methods=["GET"])
def download_file_endpoint(uuid):
    if not uuid:
        return jsonify({"error": "no uuid"}), 400
    db = get_flask_db()
    result = transcription_db.get_transcription(db, uuid)
    if not result:
        return jsonify({"error": "not found"}), 404
    fn = get_downloaded_file_path(uuid)
    if not os.path.exists(fn):
        return jsonify({"error": f"hahahah not found {fn} {uuid}"}), 404
    return send_file(fn, mimetype="audio/ogg")
