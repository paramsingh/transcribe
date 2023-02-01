import sqlite3
import uuid
import time

LINK_VALIDITY_TIME = 1 * 60 * 60  # 1 hour


def create_magic_link(db: sqlite3.Connection, user_id: int) -> str:
    token = f"ml_{str(uuid.uuid4())}"
    cursor = db.cursor()
    cursor.execute(
        """
        INSERT INTO magic_link (user_id, link_token)
        VALUES (?, ?);
        """, (user_id, token),
    )
    db.commit()
    return token


def get_valid_link(db: sqlite3.Connection, token: str) -> bool:
    cursor = db.cursor()
    cursor.execute(
        """
        SELECT id, created, user_id, redeemed
          FROM magic_link WHERE link_token = ?
        """, (token,),
    )
    data = cursor.fetchone()
    if not data:
        return None

    # TODO: Should show better error when link is expired
    if expired(data[1]):
        return None

    # already redeemed
    if data[3]:
        return None

    return {
        "id": data[0],
        "created": data[1],
        "user_id": data[2],
    }


def redeem_magic_link(db: sqlite3.Connection, link_token: str):
    cursor = db.cursor()
    cursor.execute(
        """
        UPDATE magic_link
           SET redeemed = 1,
               redeemed_at = ?
         WHERE link_token = ?
        """, (link_token, time.time()),
    )
    db.commit()


def expired(created) -> bool:
    return created < time.time() - LINK_VALIDITY_TIME
