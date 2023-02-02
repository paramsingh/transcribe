import uuid
import sqlite3
from typing import Optional


def get_session(db: sqlite3.Connection, id: int) -> Optional[dict]:
    """ Get existing session from the database """
    cursor = db.cursor()
    cursor.execute(
        """
        SELECT id, user_id, token, created FROM session WHERE id = ?;
    """,
        (id,),
    )
    session = cursor.fetchone()
    if session:
        return {
            "id": session[0],
            "user_id": session[1],
            "session_id": session[2],
            "created": session[3],
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