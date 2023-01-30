from flask import Blueprint

login_bp = Blueprint("login", __name__)


@login_bp.route("/login", methods=["POST"])
def login():
    return "login"


@login_bp.route("/session/create", methods=["POST"])
def send_email():
    pass
