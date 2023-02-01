from typing import Optional
import uuid
import sqlite3


def get_user_by_id(db: sqlite3.Connection, id: int) -> Optional[dict]:
    """ Get existing user from the database """
    cursor = db.cursor()
    cursor.execute(
        """
        SELECT id, email, user_id, created FROM user WHERE id = ?;
    """,
        (id,),
    )
    user = cursor.fetchone()
    if user:
        return {
            "id": user[0],
            "email": user[1],
            "user_id": user[2],
            "created": user[3],
        }
    return None


def get_or_create_user(db: sqlite3.Connection, email: str) -> dict:
    """Get or create a user with the given email"""
    user = get_user_by_email(db, email)
    if user:
        return user
    return create_user(db, email)


def get_user_by_email(db: sqlite3.Connection, email: str) -> Optional[dict]:
    """ Get existing user from the database """
    cursor = db.cursor()
    cursor.execute(
        """
        SELECT id, email, user_id, created FROM user WHERE email = ?;
    """,
        (email,),
    )
    user = cursor.fetchone()
    if user:
        return {
            "id": user[0],
            "email": user[1],
            "user_id": user[2],
            "created": user[3],
        }
    return None


def create_user(db: sqlite3.Connection, email: str) -> dict:
    """ Create a new user in the database """
    cursor = db.cursor()
    cursor.execute(
        """
        INSERT INTO user (email, user_id)
        VALUES (?, ?);
    """,
        (email, f"usr_{str(uuid.uuid4())}"),
    )
    db.commit()
    return get_user_by_email(db, email)
