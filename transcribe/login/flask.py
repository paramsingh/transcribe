from flask import Blueprint, request, jsonify
from flask_cors import cross_origin  # type: ignore
from transcribe.db.db_utils import get_flask_db
import transcribe.login.db.user as db_user
import transcribe.login.db.session as db_session
import transcribe.login.db.magic_link as db_magic_link

login_bp = Blueprint("login", __name__)


@login_bp.route("/send-email", methods=["POST"])
@cross_origin()
def send_email_endpoint():
    data = request.get_json()
    email = data.get("email")
    if not email:
        return jsonify({"error": "no email"}), 400
    db = get_flask_db()

    user = db_user.get_or_create_user(db, email)
    magic_link = db_magic_link.create_magic_link(db, user['id'])
    # TODO: send email with link
    return jsonify({"success": True, "token": magic_link})


@login_bp.route("/redeem-magic-link", methods=["POST"])
@cross_origin()
def redeem_magic_link_endpoint():
    data = request.get_json()
    magic_link = data.get("secret")
    if not magic_link:
        return jsonify({"error": "no secret passed"}), 400
    db = get_flask_db()

    valid_link = db_magic_link.get_valid_link(db, magic_link)
    if not valid_link:
        return jsonify({"error": "invalid secret"}), 400

    user = db_user.get_user_by_id(db, valid_link['user_id'])
    if not user:
        return jsonify({"error": "invalid secret"}), 400

    session = db_session.create_session(db, user)
    db_magic_link.redeem_magic_link(db, magic_link, session['id'])
    return jsonify({"session": session['session_id']})
