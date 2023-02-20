import typing
import os

from flask_cors import cross_origin  # type: ignore
from flask import Blueprint, jsonify, Response, request, send_file
from gpt_index import GPTSimpleVectorIndex

from transcribe.db.db_utils import get_flask_db
import transcribe.login.db.session as db_session
import transcribe.db.transcription as transcription_db
import transcribe.db.embedding as embedding_db
from transcribe.processor.transcribe import get_downloaded_file_path

api_bp = Blueprint("api_v1", __name__)


def get_session_token(req) -> typing.Optional[str]:
    authorization_header = req.headers.get("Authorization")
    if not authorization_header:
        return None
    if not authorization_header.startswith("Bearer "):
        return None
    return authorization_header.split()[1]


def get_user(req) -> typing.Optional[dict]:
    session_token = get_session_token(req)
    if not session_token:
        return None
    db = get_flask_db()
    return db_session.validate_and_get_user(db, session_token)


@api_bp.route("/transcribe", methods=["POST"])
@cross_origin()
def transcribe() -> Response:
    user = get_user(request)
    user_id = user['id'] if user else None
    request_data = typing.cast(typing.Dict[str, str], request.get_json())
    link = request_data.get("link")
    if not link:
        return jsonify({"error": "no link"}), 400
    db = get_flask_db()
    existing = transcription_db.get_transcription_by_link(db, link)
    if existing:
        if existing["result"] is None and existing["transcribe_failed"]:
            transcription_db.set_transcription_failed(
                db, existing["id"], False)
        transcription_db.log_transcription_attempt(db, existing["id"], user_id)
        return existing["token"]
    token = transcription_db.create_transcription(db, link, user_id, None)
    return jsonify({"id": token})


@api_bp.route("/transcription/<token>/details", methods=["GET"])
@cross_origin()
def get_transcription(token) -> Response:
    if not token:
        return jsonify({"error": "no token"}), 400
    db = get_flask_db()
    result = transcription_db.get_transcription(db, token)
    if not result:
        return jsonify({"error": "not found"}), 404
    result['has_embeddings'] = embedding_db.has_embeddings(db, result['id'])
    return jsonify(result)


@api_bp.route("/user/<token>/transcriptions", methods=["GET"])
@cross_origin()
def get_user_transcriptions(token) -> Response:
    if not token:
        return jsonify({"error": "no token"}), 400
    db = get_flask_db()
    user = get_user(request)
    if user is None:
        return jsonify({"error": "unauthorized"}), 401
    if user['token'] != token:
        return jsonify({"error": "unauthorized"}), 401
    attempts = transcription_db.get_user_transcription_attempts(db, user['id'])
    return jsonify({"transcriptions": attempts})


@api_bp.route("/recent-transcriptions", methods=["GET"])
@cross_origin()
def get_recent_transcriptions_endpoint():
    transcriptions = transcription_db.get_recent_transcriptions(get_flask_db())
    return jsonify({"transcriptions": transcriptions})


@api_bp.route("/internal/transcription/<token>/file", methods=["GET"])
def download_file_endpoint(token: str):
    if not token:
        return jsonify({"error": "no token"}), 400
    db = get_flask_db()
    result = transcription_db.get_transcription(db, token)
    if not result:
        return jsonify({"error": "not found"}), 404
    fn = get_downloaded_file_path(token)
    if not os.path.exists(fn):
        return jsonify({"error": f"file not found: {token}"}), 404
    return send_file(fn, mimetype="audio/ogg")


@api_bp.route("/transcription/<token>/ask", methods=["POST"])
@cross_origin()
def ask(token: str):
    if not token:
        return jsonify({"error": "no token"}), 400
    request_data = typing.cast(typing.Dict[str, str], request.get_json())
    question = request_data.get("question")
    if not question:
        return jsonify({"error": "no question"}), 400

    db = get_flask_db()
    transcription = transcription_db.get_transcription(db, token)
    if transcription is None:
        return jsonify({"error": "not found"}), 404
    embeddings = embedding_db.get_embeddings_for_transcription(
        db, transcription['id'])
    index = GPTSimpleVectorIndex.load_from_string(embeddings['embedding_json'])
    answer = index.query(question)
    return jsonify({"answer": str(answer)})
