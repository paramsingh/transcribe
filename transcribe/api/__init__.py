import typing

from flask_cors import cross_origin  # type: ignore
from flask import Blueprint, jsonify, Response, request

api_bp = Blueprint("api_v1", __name__)


@api_bp.route("/transcribe", methods=["POST"])
@cross_origin()
def transcribe() -> Response:
    request_data = typing.cast(typing.Dict[str, str], request.get_json())
    # TODO: push to the queue and the db
    return jsonify({"id": "uuid"})
