import json
import time
import typing
from typing import Union
import os
from uuid import uuid4

from flask_cors import cross_origin  # type: ignore
from flask import Blueprint, jsonify, Response, request, send_file
from gpt_index import GPTSimpleVectorIndex

from transcribe.db.db_utils import get_flask_db, get_pinecone_index, get_s2_connection
from transcribe.chat.insert_into_s2 import get_answer
import transcribe.login.db.session as db_session
import transcribe.db.transcription as transcription_db
import transcribe.db.embedding as embedding_db
from transcribe.processor.transcribe import get_downloaded_file_path
from transcribe.processor.utils import is_group_link, get_group_items, is_group_token, get_youtube_video_length

api_bp = Blueprint("api_v1", __name__)

MAX_LENGTH_ALLOWED_FOR_UNAUTHENTICATED_SUBMISSION = 20 * 60  # 20 minutes
MAX_LENGTH_ALLOWED_PER_VIDEO = 4 * 60 * 60  # 4 hours


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


def get_source_video_link(gpt_response):
    try:
        source_text = gpt_response.source_nodes[0].source_text
        first_line = source_text.split('\n')[0]
        # this line looks like "doc id: https://youtube.com/watch?id=blah"
        return first_line.split(': ')[-1].strip()
    except:
        return None


@api_bp.route("/transcribe", methods=["POST"])
@cross_origin()
def transcribe() -> Response:
    request_data = typing.cast(typing.Dict[str, str], request.get_json())
    link = request_data.get("link")
    user = get_user(request)
    user_id = user['id'] if user else None

    # don't allow group links for unauthenticated users
    if is_group_link(link) and not user:
        return jsonify({"error": "group links require login", "code": "GROUP_LINKS_NEED_LOGIN"}), 400

    video_length = get_youtube_video_length(link)

    # don't allow videos longer than 4 hours, regardless of user
    if video_length > MAX_LENGTH_ALLOWED_PER_VIDEO:
        return jsonify({"error": "video too long", "code": "VIDEO_TOO_LONG"}), 400

    # don't allow videos longer than 20 minutes for unauthenticated users
    if not user and video_length > MAX_LENGTH_ALLOWED_FOR_UNAUTHENTICATED_SUBMISSION:
        return jsonify({"error": "video too long, needs login", "code": "VIDEO_TOO_LONG_FOR_UNAUTHENTICATED"}), 400

    if not link:
        return jsonify({"error": "no link", "code": "NO_LINK"}), 400
    db = get_flask_db()
    existing = transcription_db.get_transcription_by_link(db, link)
    if existing:
        if existing["result"] is None and existing["transcribe_failed"]:
            transcription_db.set_transcription_failed(
                db, existing["id"], False)
        transcription_db.log_transcription_attempt(db, existing["id"], user_id)
        return jsonify({"id": existing["token"]})
    token = create_transcription(db, link, user_id)
    return jsonify({"id": token})


def create_transcription(db, link: str, user_id: int) -> str:
    _token = transcription_db.get_token_if_existing(db, link, user_id)
    if _token:
        return _token
    if is_group_link(link):
        token = f"gr-{str(uuid4())}"
        transcription_db.create_transcriptions_with_group(
            db, get_group_items(link), user_id, token, link)
    else:
        result_json = None
        token = transcription_db.create_transcription_with_transcription_token(
            db, link, user_id, result_json)
    return token


@api_bp.route("/transcription/<token>/details", methods=["GET"])
@cross_origin()
def get_transcription(token) -> Response:
    if not token:
        return jsonify({"error": "no token"}), 400
    db = get_flask_db()
    if is_group_token(token):
        result = transcription_db.get_transcription_group(db, token)
    else:
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
    if token == 'yc':
        index = get_pinecone_index()
        answer = index.query(question)
        source_video_link = get_source_video_link(answer)
        transcription = transcription_db.get_transcription_by_link(
            db,
            source_video_link,
        )
        return jsonify({
            "answer": str(answer),
            "sources": [
                {
                    "video": get_source_video_link(answer),
                    "transcription_token": transcription['token'],
                },
            ],
        })
    elif token == 'yc-s2':
        t = time.time()
        connection = get_s2_connection()
        print(f"took {time.time() - t} to get connection")

        answer, source = get_answer(connection, question)
        print(
            f"endpoint took a total of {time.time() - t} to get final answer")
        return jsonify({
            "answer": str(answer),
            "sources": [
                {
                    "video": source,
                    "transcription_token": transcription_db.get_transcription_by_link(db, source)['token'],
                }
            ]
        })
    else:
        transcription = transcription_db.get_transcription(db, token)
        if transcription is None:
            return jsonify({"error": "not found"}), 404
        embeddings = embedding_db.get_embeddings_for_transcription(
            db, transcription['id'])
        index = GPTSimpleVectorIndex.load_from_string(
            embeddings['embedding_json'])
        answer = index.query(question)
        return jsonify({"answer": str(answer)})
