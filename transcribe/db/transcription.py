from uuid import uuid4
from transcribe.db import init_db
from typing import Union


def get_transcription(db, token: str) -> Union[dict, None]:
    cursor = db.cursor()

    cursor.execute(
        """
        SELECT token, link, result, improvement, summary FROM transcription WHERE token = ?;
    """,
        (token,),
    )
    result = cursor.fetchone()

    if result:
        return {
            "token": result[0],
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
        SELECT token, link, result FROM transcription WHERE link = ?;
    """,
        (link,),
    )
    result = cursor.fetchone()

    if result:
        return {
            "token": result[0],
            "link": result[1],
            "result": result[2],
        }
    return None


def get_one_unfinished_transcription(db) -> Union[dict, None]:
    cursor = db.cursor()
    cursor.execute(
        """
        SELECT token, link
          FROM transcription
         WHERE result is NULL
           AND transcribe_failed = 0
         LIMIT 1;
    """
    )
    result = cursor.fetchone()

    if result:
        return {"token": result[0], "link": result[1]}
    return None


def get_one_unimproved_transcription(db) -> Union[dict, None]:
    cursor = db.cursor()
    cursor.execute(
        """
        SELECT token, link, result, improvement, summary
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
            "token": result[0],
            "link": result[1],
            "result": result[2],
            "improvement": result[3],
            "summary": result[4],
        }
    return None


def add_improvement(db, improved_text: str, token: str) -> None:
    """Add improved text to the improvement column for transcription with given token"""
    cursor = db.cursor()
    cursor.execute(
        """
        UPDATE transcription SET improvement = ? WHERE token = ?;
    """,
        (improved_text, token),
    )
    db.commit()


def mark_improvement_failed(db, token: str) -> None:
    """Mark transcription as failed improvement"""
    cursor = db.cursor()
    cursor.execute(
        """
        UPDATE transcription SET improvement_failed = 1 WHERE token = ?;
    """,
        (token,),
    )
    db.commit()


def mark_transcription_failed(db, token: str) -> None:
    cursor = db.cursor()
    cursor.execute(
        """
        UPDATE transcription SET transcribe_failed = 1 WHERE token = ?;
    """,
        (token,),
    )
    db.commit()


def add_summary(db, summary: str, token: str) -> None:
    """Add summary to the summary column for transcription with given token"""
    cursor = db.cursor()
    cursor.execute(
        """
        UPDATE transcription SET summary = ? WHERE token = ?;
    """,
        (summary, token),
    )
    db.commit()


def populate_transcription(db, token: str, result: str) -> None:
    """Add result to a transcription"""
    cursor = db.cursor()
    cursor.execute(
        """
        UPDATE transcription SET result = ? WHERE token = ?;
    """,
        (result, token),
    )
    db.commit()


def create_transcription(db, link: str, user_id: int, result: str) -> str:
    cursor = db.cursor()

    existing = get_transcription_by_link(db, link)
    if existing:
        return existing["token"]

    token = f"tr-{str(uuid4())}"
    cursor.execute(
        """
        INSERT INTO transcription (token, link, user_id, result) VALUES (?, ?, ?, ?);
    """,
        (token, link, user_id, result),
    )
    db.commit()
    return token
