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
    transcription_db.create_transcription(link, None)
    # TODO: push to the queue
    return jsonify({"id": "uuid"})
