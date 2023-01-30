from uuid import uuid4
from transcribe.db import init_db
from typing import Union


def get_transcription(db, uuid: str) -> Union[dict, None]:
    cursor = db.cursor()

    cursor.execute(
        """
        SELECT uuid, link, result, improvement, summary FROM transcription WHERE uuid = ?;
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
            "summary": result[4],
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
        SELECT uuid, link, result, improvement, summary
          FROM transcription
         WHERE (improvement is NULL OR summary IS NULL)
           AND result is NOT NULL
           AND improvement_failed = 0
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
            "improvement": result[3],
            "summary": result[4],
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


def mark_improvement_failed(db, uuid: str) -> None:
    """Mark transcription as failed improvement"""
    cursor = db.cursor()
    cursor.execute(
        """
        UPDATE transcription SET improvement_failed = 1 WHERE uuid = ?;
    """,
        (uuid,),
    )
    db.commit()


def add_summary(db, summary: str, uuid: str) -> None:
    """Add summary to the summary column for transcription with given UUID"""
    cursor = db.cursor()
    cursor.execute(
        """
        UPDATE transcription SET summary = ? WHERE uuid = ?;
    """,
        (summary, uuid),
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
