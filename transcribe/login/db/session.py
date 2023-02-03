import uuid
import sqlite3
from typing import Optional
from transcribe.login.db.user import get_user_by_id


def get_session(db: sqlite3.Connection, id: int) -> Optional[dict]:
    """ Get existing session from the database """
    cursor = db.cursor()
    cursor.execute(
        """
        SELECT id, user_id, token, logged_out, created FROM session WHERE id = ?;
    """,
        (id,),
    )
    session = cursor.fetchone()
    if session:
        return {
            "id": session[0],
            "user_id": session[1],
            "session_id": session[2],
            "logged_out": session[3],
            "created": session[4],
        }
    return None


def create_session(db, user):
    """ Create a new session in the database """
    token = f"session-{str(uuid.uuid4())}"
    cursor = db.cursor()
    cursor.execute(
        """
        INSERT INTO session (user_id, token)
        VALUES (?, ?);
    """,
        (user["id"], token),
    )
    db.commit()
    return get_session(db, cursor.lastrowid)


def get_session_by_token(db, token):
    cursor = db.cursor()
    cursor.execute(
        """
        SELECT id, user_id, token, logged_out, created FROM session WHERE token = ?;
    """,
        (token,),
    )
    session = cursor.fetchone()
    if session:
        return {
            "id": session[0],
            "user_id": session[1],
            "session_id": session[2],
            "logged_out": session[3],
            "created": session[4],
        }
    return None


def validate_and_get_user(db: sqlite3.Connection, session_token: str) -> Optional[dict]:
    session = get_session_by_token(db, session_token)
    if not session:
        return None
    if session["logged_out"]:
        return None
    return get_user_by_id(db, session["user_id"])


def log_out_session(db: sqlite3.Connection, session_token: str):
    cursor = db.cursor()
    cursor.execute(
        """
        UPDATE session
           SET logged_out = 1,
               logged_out_at = datetime('now')
         WHERE token = ?;
    """,
        (session_token,),
    )
    db.commit()
