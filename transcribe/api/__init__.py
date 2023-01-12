import typing

from flask_cors import cross_origin  # type: ignore
from flask import Blueprint, jsonify, Response, request
import transcribe.db.transcription as transcription_db

api_bp = Blueprint("api_v1", __name__)


@api_bp.route("/transcribe", methods=["POST"])
@cross_origin()
def transcribe() -> Response:
    request_data = typing.cast(typing.Dict[str, str], request.get_json())
    link = request_data.get("link")
    if not link:
        return jsonify({"error": "no link"}), 400
    uuid = transcription_db.create_transcription(link, None)
    return jsonify({"id": uuid})


@api_bp.route("/transcription/<uuid>/details", methods=["GET"])
@cross_origin()
def get_transcription() -> Response:
    uuid = request.args.get("uuid")
    if not uuid:
        return jsonify({"error": "no uuid"}), 400
    result = transcription_db.get_transcription(uuid)
    if not result:
        return jsonify({"error": "not found"}), 404
    return jsonify(result)
