from uuid import uuid4
from transcribe.db import init_db
from typing import Union


def get_transcription(db, uuid: str) -> Union[dict, None]:
    cursor = db.cursor()

    cursor.execute(
        """
        SELECT uuid, link, result, improvement FROM transcription WHERE uuid = ?;
    """,
        (uuid,),
    )
    result = cursor.fetchone()

    if result:
        return {
            "uuid": result[0],
            "link": result[1],
            "result": result[2],
            "improvement": result[3],
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
    cursor.execute(
        """
        SELECT uuid, link FROM transcription WHERE result is NULL LIMIT 1;
    """
    )
    result = cursor.fetchone()

    if result:
        return {"uuid": result[0], "link": result[1]}
    return None


def get_one_unimproved_transcription(db) -> Union[dict, None]:
    cursor = db.cursor()
    cursor.execute(
        """
        SELECT uuid, link, result
          FROM transcription
         WHERE improvement is NULL
           AND result is NOT NULL
      ORDER BY created ASC
         LIMIT 1;
    """
    )
    result = cursor.fetchone()

    if result:
        return {
            "uuid": result[0],
            "link": result[1],
            "result": result[2],
        }
    return None


def add_improvement(db, improved_text: str, uuid: str) -> None:
    """Add improved text to the improvement column for transcription with given UUID"""
    cursor = db.cursor()
    cursor.execute(
        """
        UPDATE transcription SET improvement = ? WHERE uuid = ?;
    """,
        (improved_text, uuid),
    )
    db.commit()


def populate_transcription(db, uuid: str, result: str) -> None:
    """Add result to a transcription"""
    cursor = db.cursor()
    cursor.execute(
        """
        UPDATE transcription SET result = ? WHERE uuid = ?;
    """,
        (result, uuid),
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
