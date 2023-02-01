import sqlite3
import uuid
import datetime

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


def redeem_magic_link(db: sqlite3.Connection, link_token: str, session_id: int):
    cursor = db.cursor()
    cursor.execute(
        """
        UPDATE magic_link
           SET redeemed = 1,
               redeemed_at = ?,
               session_id = ?
         WHERE link_token = ?
        """, (datetime.datetime.now(), session_id, link_token),
    )
    db.commit()


def expired(created: datetime.datetime) -> bool:
    return created >= datetime.datetime.now() - datetime.timedelta(seconds=LINK_VALIDITY_TIME)
