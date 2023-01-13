from uuid import uuid4
from transcribe.db import init_db
from typing import Union


def get_transcription(db, uuid: str) -> Union[dict, None]:
    cursor = db.cursor()

    cursor.execute(
        """
        SELECT uuid, link, result FROM transcription WHERE uuid = ?;
    """,
        (uuid,),
    )
    result = cursor.fetchone()

    if result:
        return {
            "uuid": result[0],
            "link": result[1],
            "result": result[2],
        }
    return None


def get_transcription_by_link(db, link):
    cursor = db.cursor()

    cursor.execute(
        """
        SELECT uuid, link, result FROM transcription WHERE link = ?;
    """,
        (link,),
    )
    result = cursor.fetchone()

    if result:
        return {
            "uuid": result[0],
            "link": result[1],
            "result": result[2],
        }
    return None


def get_one_unfinished_transcription(db) -> Union[dict, None]:
    cursor = db.cursor()
    cursor.execute("""
        SELECT uuid, link FROM transcription WHERE result is NULL LIMIT 1;
    """)
    result = cursor.fetchone()

    if result:
        return {
            "uuid": result[0],
            "link": result[1]
        }
    return None


def populate_transcription(db, uuid: str, result: str) -> None:
    cursor = db.cursor()

    cursor.execute(
        """
        INSERT INTO transcription (result) VALUES (?) WHERE uuid = ?;
    """,
        (uuid, result),
    )
    db.commit()


def create_transcription(db, link: str, result: str) -> str:
    cursor = db.cursor()

    existing = get_transcription_by_link(db, link)
    if existing:
        return existing["uuid"]

    uuid = str(uuid4())
    cursor.execute(
        """
        INSERT INTO transcription (uuid, link, result) VALUES (?, ?, ?);
    """,
        (uuid, link, result),
    )
    db.commit()
    return uuid
